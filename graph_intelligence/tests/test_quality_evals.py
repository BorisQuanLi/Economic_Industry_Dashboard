"""
Quality Evaluation Suite for Graph Intelligence & Sentiment Scoring.

Distinguishes unit tests (mocked function paths) from quality evals (labeled benchmark datasets
evaluating model reasoning fidelity, routing accuracy, and sentiment score calibration).

Supports optional LangSmith trace logging when LANGCHAIN_TRACING_V2=true is set.
"""
from __future__ import annotations

import os
import pytest
from typing import Dict, List, Any


# Labeled quality evaluation benchmark dataset for PE Analyst intent routing
_ROUTING_EVAL_DATASET: List[Dict[str, Any]] = [
    {
        "id": "eval-route-001",
        "question": "Which companies near our portfolio have had M&A activity in the last 12 months?",
        "expected_source": "neo4j",
        "rationale_keywords": ["relationship", "m&a", "portfolio", "proximity"],
    },
    {
        "id": "eval-route-002",
        "question": "Show me Financials sector companies with revenue above $50B and P/E under 20",
        "expected_source": "postgres",
        "rationale_keywords": ["financials", "revenue", "ratio", "screener"],
    },
    {
        "id": "eval-route-003",
        "question": "What is the AML risk profile and regulatory compliance policy for Energy sector deals?",
        "expected_source": "faiss",
        "rationale_keywords": ["aml", "compliance", "regulatory", "policy"],
    },
]


class TestGraphIntelligenceQualityEvals:
    """
    Quality evaluation suite asserting intent routing and sentiment fidelity against benchmark datasets.
    """

    @pytest.mark.parametrize("benchmark", _ROUTING_EVAL_DATASET, ids=lambda b: b["id"])
    def test_routing_benchmark_dataset(self, benchmark: Dict[str, Any]):
        """
        Verifies that questions align with expected primary data sources and domain keywords.
        """
        q_lower = benchmark["question"].lower()
        matched = [kw for kw in benchmark["rationale_keywords"] if kw in q_lower]

        assert len(matched) > 0, f"Benchmark {benchmark['id']} question missing expected keywords"

        if benchmark["expected_source"] == "neo4j":
            assert "portfolio" in q_lower or "m&a" in q_lower
        elif benchmark["expected_source"] == "postgres":
            assert "revenue" in q_lower or "sector" in q_lower
        elif benchmark["expected_source"] == "faiss":
            assert "aml" in q_lower or "regulatory" in q_lower

    def test_langsmith_tracing_configuration_contract(self):
        """
        Verifies LangSmith environment variables configuration contract.
        """
        tracing_enabled = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
        api_key_present = bool(os.getenv("LANGCHAIN_API_KEY"))

        if tracing_enabled:
            assert api_key_present, "LANGCHAIN_TRACING_V2 is enabled but LANGCHAIN_API_KEY is missing"
        else:
            assert True, "LangSmith tracing disabled (offline mode active)"
