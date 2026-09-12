"""Orchestrates intent extraction, governed retrieval, and grounded answers."""
from __future__ import annotations

from graph_intelligence.nlp_search.answer_service import DeterministicAnswerService
from graph_intelligence.nlp_search.intent_extractor import IntentExtractor
from graph_intelligence.nlp_search.retrieval import FinancialFixtureRetriever
from graph_intelligence.nlp_search.schemas import AnalystAnswer


class NlpSearchService:
    """Single entry point for the credential-free natural-language search MVP."""

    def __init__(
        self,
        intent_extractor: IntentExtractor,
        retriever: FinancialFixtureRetriever,
        answer_service: DeterministicAnswerService,
    ) -> None:
        self._intent_extractor = intent_extractor
        self._retriever = retriever
        self._answer_service = answer_service

    def search(self, question: str) -> AnalystAnswer:
        intent = self._intent_extractor.extract(question)
        records = self._retriever.retrieve(intent)
        return self._answer_service.render(question, records)
