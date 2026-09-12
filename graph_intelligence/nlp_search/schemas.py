"""Closed data contracts for the natural-language financial-search workflow."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class FinancialSearchIntent(BaseModel):
    """Validated, provider-neutral representation of an analyst's question.

    The model is intentionally unable to carry arbitrary SQL, Cypher, or tool
    names. Retrieval code maps these allowlisted fields to bound parameters.
    """

    model_config = ConfigDict(extra="forbid")

    query_type: Literal["company_screen", "sector_comparison", "relationship_search"]
    sectors: list[str]
    tickers: list[str]
    max_pe_ratio: float | None = Field(ge=0)
    min_revenue_usd_bn: float | None = Field(ge=0)
    include_relationship_signal: bool
    rationale: str = Field(min_length=1, max_length=500)


class RetrievedRecord(BaseModel):
    """A source record made available to deterministic or LLM answer rendering."""

    model_config = ConfigDict(extra="forbid")

    source: Literal["financial_fixture", "graph_fixture"]
    record_id: str = Field(min_length=1)
    ticker: str
    data: dict[str, Any]


class AnalystAnswer(BaseModel):
    """Grounded answer returned by the first vertical slice."""

    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=1)
    answer: str
    citations: list[str]
    records: list[RetrievedRecord]
