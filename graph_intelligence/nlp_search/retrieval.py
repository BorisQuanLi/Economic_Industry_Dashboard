"""Allowlisted retrieval over deterministic financial and graph fixtures."""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from graph_intelligence.nlp_search.schemas import FinancialSearchIntent, RetrievedRecord


FINANCIAL_FIXTURES: tuple[dict[str, Any], ...] = (
    {
        "ticker": "CRM",
        "sector": "Information Technology",
        "avg_pe_ratio": 22.5,
        "latest_revenue_usd_bn": 31.4,
    },
    {
        "ticker": "ORCL",
        "sector": "Information Technology",
        "avg_pe_ratio": 18.3,
        "latest_revenue_usd_bn": 50.0,
    },
    {
        "ticker": "IBM",
        "sector": "Information Technology",
        "avg_pe_ratio": 14.1,
        "latest_revenue_usd_bn": 60.5,
    },
)

GRAPH_FIXTURES: dict[str, dict[str, Any]] = {
    "CRM": {"proximity_score": 4, "path_type": "INSTITUTIONAL_HOLDER"},
    "ORCL": {"proximity_score": 2, "path_type": "MA_HISTORY"},
    "IBM": {"proximity_score": 1, "path_type": "BOARD_CONNECTION"},
}


class FinancialFixtureRetriever:
    """Maps validated intent fields to deterministic retrieval predicates.

    This mirrors the eventual parameterized data-access layer without accepting
    raw LLM-generated query fragments.
    """

    def __init__(self, rows: Sequence[dict[str, Any]] = FINANCIAL_FIXTURES) -> None:
        self._rows = tuple(dict(row) for row in rows)

    def retrieve(self, intent: FinancialSearchIntent) -> list[RetrievedRecord]:
        records: list[RetrievedRecord] = []
        allowed_sectors = {sector.casefold() for sector in intent.sectors}
        allowed_tickers = {ticker.upper() for ticker in intent.tickers}

        for row in self._rows:
            if allowed_sectors and row["sector"].casefold() not in allowed_sectors:
                continue
            if allowed_tickers and row["ticker"].upper() not in allowed_tickers:
                continue
            if intent.max_pe_ratio is not None and row["avg_pe_ratio"] > intent.max_pe_ratio:
                continue
            if (
                intent.min_revenue_usd_bn is not None
                and row["latest_revenue_usd_bn"] < intent.min_revenue_usd_bn
            ):
                continue

            data = dict(row)
            if intent.include_relationship_signal:
                data["relationship"] = GRAPH_FIXTURES.get(row["ticker"], {})
            records.append(
                RetrievedRecord(
                    source="financial_fixture",
                    record_id=f"financial:{row['ticker']}",
                    ticker=row["ticker"],
                    data=data,
                )
            )

        return sorted(
            records,
            key=lambda record: record.data["latest_revenue_usd_bn"],
            reverse=True,
        )
