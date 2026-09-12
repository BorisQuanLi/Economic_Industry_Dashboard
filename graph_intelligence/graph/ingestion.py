"""
Graph ingestion: public M&A and institutional ownership data → Neo4j edges.

Data sourced from SEC filings (13F institutional holder disclosures, M&A
transaction records) via a financial data vendor API.  The vendor is
configurable via FMP_API_KEY and FMP_BASE env vars; the ingestion pattern
(rate-limiting, 429-retry, RUN_GRAPH_INGESTION gate) is vendor-agnostic.

Relationship types created
--------------------------
(Company)-[:ACQUIRED {date}]->(Company)
    Source: M&A transaction feed.
    Powers score_deal_proximity() — companies with shared M&A history
    appear within 2 hops of each other in the relationship graph.

(Institution)-[:HOLDS {shares, reported_date}]->(Company)
    Source: SEC 13F institutional holder disclosures.
    Powers both score_deal_proximity() (shared holders = proximity) and
    portfolio contagion risk analysis (correlated stress via shared holders).

Rate-limiting
-------------
Financial data vendor free tier: 250 calls/day.  Sleeps 1 second between
ticker-level calls; retries once on HTTP 429.

Safety gate
-----------
Both ingest functions raise RuntimeError if RUN_GRAPH_INGESTION != 'true'.
This function must never run in CI, in the demo path, or on import.

Error handling
--------------
A failed individual record does not abort the ingestion run — the loop logs
the error with context and continues.  Caller receives a count of edges
successfully written.
"""
from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

FMP_KEY = os.getenv("FMP_API_KEY", "")
FMP_BASE = os.getenv("FMP_BASE", "https://financialmodelingprep.com/api")

_CALL_INTERVAL_SECONDS = 1.0
_RETRY_ON_429 = True


async def _vendor_get(
    client: httpx.AsyncClient, url: str, params: dict
) -> list[Any]:
    """Single vendor API GET with one 429-retry.  Returns parsed JSON list or []."""
    for attempt in range(2):
        try:
            resp = await client.get(
                url, params={**params, "apikey": FMP_KEY}, timeout=10.0
            )
        except httpx.RequestError as exc:
            logger.warning(
                "Vendor API request error (attempt %d): %s", attempt + 1, exc
            )
            return []

        if resp.status_code == 200:
            data = resp.json()
            return data if isinstance(data, list) else []

        if resp.status_code == 429 and _RETRY_ON_429 and attempt == 0:
            logger.warning("Vendor API 429 rate limit — sleeping 60 s before retry")
            await asyncio.sleep(60)
            continue

        logger.warning("Vendor API HTTP %d for %s", resp.status_code, url)
        return []

    return []


async def ingest_ma_edges(neo4j_client: Any, tickers: list[str]) -> int:
    """
    Fetch M&A transaction records and write (Company)-[:ACQUIRED]->(Company) edges.

    Parameters
    ----------
    neo4j_client : Neo4jClient instance
    tickers      : scope ingestion to edges involving these tickers;
                   pass [] to ingest all deals in the feed

    Returns
    -------
    Number of edges written.

    Raises
    ------
    RuntimeError if RUN_GRAPH_INGESTION != 'true'.
    """
    if os.getenv("RUN_GRAPH_INGESTION", "false").lower() != "true":
        raise RuntimeError(
            "ingest_ma_edges requires RUN_GRAPH_INGESTION=true.  "
            "This function must not run in CI or the demo path."
        )

    driver = neo4j_client._get_driver()
    edges_written = 0

    async with httpx.AsyncClient() as http_client:
        deals = await _vendor_get(
            http_client,
            f"{FMP_BASE}/v4/mergers-acquisitions-rss-feed",
            {"limit": 100},
        )
        logger.info("M&A feed: %d transaction records fetched", len(deals))

        for deal in deals:
            acq = (deal.get("acquirerSymbol") or "").upper().strip()
            tgt = (deal.get("targetSymbol") or "").upper().strip()
            date = deal.get("date", "")

            if tickers and acq not in tickers and tgt not in tickers:
                continue
            if not acq or not tgt:
                continue

            try:
                async with driver.session() as session:
                    await session.run(
                        """
                        MERGE (a:Company {ticker: $acq})
                        MERGE (t:Company {ticker: $tgt})
                        MERGE (a)-[r:ACQUIRED]->(t)
                        ON CREATE SET r.date = $date, r.created_at = datetime()
                        ON MATCH  SET r.date = $date
                        """,
                        acq=acq, tgt=tgt, date=date,
                    )
                edges_written += 1
            except Exception:
                logger.error(
                    "Failed to write ACQUIRED edge %s->%s", acq, tgt, exc_info=True
                )

        await asyncio.sleep(_CALL_INTERVAL_SECONDS)

    logger.info("M&A ingestion complete: %d edges written", edges_written)
    return edges_written


async def ingest_institutional_edges(
    neo4j_client: Any, tickers: list[str]
) -> int:
    """
    Fetch SEC 13F institutional holder disclosures and write
    (Institution)-[:HOLDS]->(Company) edges.

    Parameters
    ----------
    neo4j_client : Neo4jClient instance
    tickers      : company tickers to ingest holders for

    Returns
    -------
    Total edges written across all tickers.

    Raises
    ------
    RuntimeError if RUN_GRAPH_INGESTION != 'true'.
    """
    if os.getenv("RUN_GRAPH_INGESTION", "false").lower() != "true":
        raise RuntimeError(
            "ingest_institutional_edges requires RUN_GRAPH_INGESTION=true."
        )

    driver = neo4j_client._get_driver()
    total_edges = 0

    async with httpx.AsyncClient() as http_client:
        for ticker in tickers:
            try:
                holders = await _vendor_get(
                    http_client,
                    f"{FMP_BASE}/v3/institutional-holder/{ticker}",
                    {},
                )
                logger.info(
                    "Ticker %s: %d institutional holders fetched",
                    ticker, len(holders),
                )

                for h in holders:
                    name = (h.get("holder") or "").strip()
                    shares = h.get("shares", 0)
                    reported = h.get("dateReported", "")
                    if not name:
                        continue

                    async with driver.session() as session:
                        await session.run(
                            """
                            MERGE (i:Institution {name: $name})
                            MERGE (c:Company {ticker: $ticker})
                            MERGE (i)-[r:HOLDS]->(c)
                            ON CREATE SET r.shares        = $shares,
                                          r.reported_date = $reported,
                                          r.created_at    = datetime()
                            ON MATCH  SET r.shares        = $shares,
                                          r.reported_date = $reported
                            """,
                            name=name,
                            ticker=ticker.upper(),
                            shares=shares,
                            reported=reported,
                        )
                    total_edges += 1

            except Exception:
                logger.error(
                    "Failed to ingest holders for %s", ticker, exc_info=True
                )

            await asyncio.sleep(_CALL_INTERVAL_SECONDS)

    logger.info(
        "Institutional holder ingestion complete: %d edges across %d tickers",
        total_edges, len(tickers),
    )
    return total_edges
