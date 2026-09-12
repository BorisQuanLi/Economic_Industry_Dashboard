"""Injected intent-extraction boundary for LLM API providers and test doubles."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol

from graph_intelligence.nlp_search.schemas import FinancialSearchIntent


class IntentExtractor(Protocol):
    """Extract a closed search intent from an analyst question."""

    def extract(self, question: str) -> FinancialSearchIntent: ...


class FakeIntentExtractor:
    """Deterministic extractor for the offline demo and unit tests.

    A production OpenAI or Anthropic adapter will implement the same protocol,
    making credentials unnecessary for local development and CI.
    """

    def __init__(
        self,
        intents_by_question: Mapping[str, FinancialSearchIntent],
    ) -> None:
        self._intents_by_question = dict(intents_by_question)

    def extract(self, question: str) -> FinancialSearchIntent:
        try:
            return self._intents_by_question[question]
        except KeyError as exc:
            raise ValueError(f"No offline intent fixture for question: {question!r}") from exc
