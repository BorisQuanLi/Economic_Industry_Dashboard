"""Offline contracts for the LLM API-backed NLP search vertical slice."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from graph_intelligence.nlp_search.answer_service import DeterministicAnswerService
from graph_intelligence.nlp_search.intent_extractor import FakeIntentExtractor
from graph_intelligence.nlp_search.retrieval import FinancialFixtureRetriever
from graph_intelligence.nlp_search.schemas import FinancialSearchIntent
from graph_intelligence.nlp_search.service import NlpSearchService


QUESTION = "Which Technology companies have P/E below 25 and revenue above $30B?"


def _intent(**overrides: object) -> FinancialSearchIntent:
    values: dict[str, object] = {
        "query_type": "company_screen",
        "sectors": ["Information Technology"],
        "tickers": [],
        "max_pe_ratio": 25.0,
        "min_revenue_usd_bn": 30.0,
        "include_relationship_signal": True,
        "rationale": "Screen Technology companies by valuation and revenue.",
    }
    values.update(overrides)
    return FinancialSearchIntent(**values)


def _service(intent: FinancialSearchIntent) -> NlpSearchService:
    return NlpSearchService(
        intent_extractor=FakeIntentExtractor({QUESTION: intent}),
        retriever=FinancialFixtureRetriever(),
        answer_service=DeterministicAnswerService(),
    )


def test_search_returns_grounded_records_and_citations() -> None:
    answer = _service(_intent()).search(QUESTION)

    assert [record.ticker for record in answer.records] == ["IBM", "ORCL", "CRM"]
    assert answer.citations == ["financial:IBM", "financial:ORCL", "financial:CRM"]
    assert "relationship score" in answer.answer


def test_no_result_has_no_citations() -> None:
    answer = _service(_intent(max_pe_ratio=10.0)).search(QUESTION)

    assert answer.records == []
    assert answer.citations == []
    assert answer.answer.startswith("No matching companies")


def test_schema_rejects_an_unallowlisted_query_field() -> None:
    with pytest.raises(ValidationError, match="extra_forbidden"):
        _intent(sql="DROP TABLE companies")


def test_fake_extractor_rejects_questions_without_a_fixture() -> None:
    with pytest.raises(ValueError, match="No offline intent fixture"):
        _service(_intent()).search("An unregistered question")
