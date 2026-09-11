"""
Async Neo4j driver wrapper for financial relationship graph queries.

Offline-safe: set USE_MOCK_GRAPH=true to return fixture data without a live
Neo4j connection — mirrors the USE_FAKE_EMBEDDINGS pattern in
mcp_agent_system/agents/rag_index.py.

Use cases
---------
find_conflict_paths
    Compliance: detect auditable relationship paths between a deal team
    and a target company through board memberships, employment history,
    or co-investment relationships.

    Why graph, not SQL: a PostgreSQL recursive CTE joining people,
    board_memberships, employment_history, and investments at depth 3
    produces combinatorial row explosion.  Neo4j traversal cost is
    proportional to the subgraph touched, not the total dataset size.

score_deal_proximity
    Sourcing: rank candidate companies by 2-hop relationship distance
    to the existing portfolio via M&A history, SEC 13F institutional
    holders, or board connections.  Closer companies have warmer
    introduction paths and more existing intelligence on file.
"""
from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Mock fixtures — domain-realistic; replicates the relationship dict from
# mcp_agent_system/demos/ma_advisory_graph_intelligence.py for the
# offline path.
# ---------------------------------------------------------------------------

_MOCK_CONFLICT_PATHS: list[dict[str, Any]] = [
    {
        "path": [
            "Advisory Team Member A",
            "TechCorp Board of Directors",
            "TargetCo",
        ],
        "relationship_types": ["BOARD_MEMBERSHIP", "BOARD_MEMBERSHIP"],
        "path_length": 2,
    },
]

_MOCK_PROXIMITY: list[dict[str, Any]] = [
    {"ticker": "CRM",  "proximity_score": 4, "path_type": "INSTITUTIONAL_HOLDER"},
    {"ticker": "ORCL", "proximity_score": 2, "path_type": "MA_HISTORY"},
    {"ticker": "IBM",  "proximity_score": 1, "path_type": "BOARD_CONNECTION"},
]


def _use_mock() -> bool:
    return os.getenv("USE_MOCK_GRAPH", "false").lower() == "true"


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

class Neo4jClient:
    """
    Async Neo4j driver wrapper.

    The driver is lazy-initialised on first query so that importing this
    module does not require a live Neo4j connection or the neo4j package.

    Offline path
    ------------
    Set USE_MOCK_GRAPH=true.  Both query methods return domain-realistic
    fixture data without requiring the neo4j package.

    Example
    -------
    >>> import os; os.environ["USE_MOCK_GRAPH"] = "true"
    >>> import asyncio
    >>> from graph_intelligence.neo4j_client import Neo4jClient
    >>> client = Neo4jClient.from_env()
    >>> asyncio.run(client.score_deal_proximity(["AAPL", "MSFT"]))
    [{'ticker': 'CRM', 'proximity_score': 4, 'path_type': 'INSTITUTIONAL_HOLDER'}, ...]
    """

    def __init__(self, uri: str, user: str, password: str) -> None:
        self._uri = uri
        self._user = user
        self._password = password
        self._driver: Any = None  # neo4j.AsyncDriver; typed Any to keep import optional

    @classmethod
    def from_env(cls) -> "Neo4jClient":
        """Construct from environment variables with sensible local defaults."""
        return cls(
            uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            user=os.getenv("NEO4J_USER", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD", "password"),
        )

    def _get_driver(self) -> Any:
        """Lazy-initialise the async driver.  Raises ImportError if neo4j absent."""
        if self._driver is None:
            try:
                from neo4j import AsyncGraphDatabase  # type: ignore[import]
            except ImportError as exc:
                raise ImportError(
                    "neo4j package is required for live connections.  "
                    "Install: pip install 'neo4j>=5.0'  "
                    "Or set USE_MOCK_GRAPH=true to run offline."
                ) from exc
            self._driver = AsyncGraphDatabase.driver(
                self._uri, auth=(self._user, self._password)
            )
        return self._driver

    async def find_conflict_paths(
        self,
        advisor_ids: list[str],
        target_ticker: str,
        max_depth: int = 3,
    ) -> list[dict[str, Any]]:
        """
        Detect auditable relationship paths between deal team members and a
        target company (board memberships, employment history, co-investments).

        Returns a list of path dicts, each with keys:
          path               — list of node names along the path
          relationship_types — list of edge type labels
          path_length        — integer hop count

        Parameters
        ----------
        advisor_ids   : list of Person node IDs in the graph
        target_ticker : Company.ticker property value
        max_depth     : maximum hop count (default 3 — standard compliance threshold)
        """
        if _use_mock():
            logger.info(
                "USE_MOCK_GRAPH=true — returning fixture conflict paths "
                "(target=%s, depth=%d)",
                target_ticker,
                max_depth,
            )
            return _MOCK_CONFLICT_PATHS

        driver = self._get_driver()
        async with driver.session() as session:
            result = await session.run(
                """
                MATCH path = (a:Person)-[*1..$depth]-(c:Company {ticker: $ticker})
                WHERE a.id IN $ids
                RETURN
                    [n IN nodes(path) | coalesce(n.name, n.ticker, toString(id(n)))]
                        AS path,
                    [r IN relationships(path) | type(r)] AS relationship_types,
                    length(path) AS path_length
                ORDER BY path_length
                LIMIT 50
                """,
                depth=max_depth,
                ticker=target_ticker,
                ids=advisor_ids,
            )
            rows: list[dict[str, Any]] = []
            async for record in result:
                rows.append({
                    "path": record["path"],
                    "relationship_types": record["relationship_types"],
                    "path_length": record["path_length"],
                })
        logger.info(
            "conflict path query: %d paths found (target=%s, depth=%d)",
            len(rows), target_ticker, max_depth,
        )
        return rows

    async def score_deal_proximity(
        self,
        portfolio_tickers: list[str],
    ) -> list[dict[str, Any]]:
        """
        Rank candidate companies by 2-hop relationship distance to the
        portfolio.  Counts distinct paths through any edge type (M&A history,
        institutional holder, board connection).

        Returns a list of dicts sorted descending by proximity_score:
          ticker           — company ticker
          proximity_score  — count of 2-hop paths from any portfolio company
          path_type        — most common relationship type among the paths

        Parameters
        ----------
        portfolio_tickers : tickers of existing portfolio companies
        """
        if _use_mock():
            logger.info(
                "USE_MOCK_GRAPH=true — returning fixture proximity scores "
                "(portfolio=%s)",
                portfolio_tickers,
            )
            return _MOCK_PROXIMITY

        driver = self._get_driver()
        async with driver.session() as session:
            result = await session.run(
                """
                MATCH (p:Company)-[r1]-(mid)-[r2]-(candidate:Company)
                WHERE p.ticker IN $tickers
                  AND NOT candidate.ticker IN $tickers
                WITH
                    candidate.ticker                 AS ticker,
                    count(*)                         AS proximity_score,
                    collect(DISTINCT type(r1))[0]    AS path_type
                RETURN ticker, proximity_score, path_type
                ORDER BY proximity_score DESC
                LIMIT 20
                """,
                tickers=portfolio_tickers,
            )
            rows: list[dict[str, Any]] = []
            async for record in result:
                rows.append({
                    "ticker": record["ticker"],
                    "proximity_score": record["proximity_score"],
                    "path_type": record["path_type"],
                })
        logger.info(
            "deal proximity query: %d candidates scored (portfolio=%s)",
            len(rows), portfolio_tickers,
        )
        return rows

    async def close(self) -> None:
        """Close the underlying driver connection pool."""
        if self._driver is not None:
            try:
                await self._driver.close()
            except Exception:
                logger.warning("Failed to close Neo4j driver cleanly", exc_info=True)
            finally:
                self._driver = None
