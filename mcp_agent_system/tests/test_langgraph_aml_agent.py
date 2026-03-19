"""Tests for LangGraph AML agent state transitions."""
from unittest.mock import MagicMock

import pytest

from agents.langgraph_aml_agent import build_aml_graph, HIGH_RISK_FLAG


def _make_graph(aml_risk_flag: str):
    mock_retriever = MagicMock()
    mock_retriever.invoke.return_value = [
        MagicMock(
            page_content=f"Sector: Finance. AML risk: {aml_risk_flag}.",
            metadata={"aml_risk_flag": aml_risk_flag},
        )
    ]
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(content="Finance sector assessed.")
    return build_aml_graph(mock_retriever, mock_llm)


def test_high_risk_routes_to_escalate():
    graph = _make_graph(HIGH_RISK_FLAG)
    result = graph.invoke({"query": "Which sectors are high AML risk?"})
    assert result["aml_risk_flag"] == HIGH_RISK_FLAG
    assert result["response"].startswith("[ESCALATED]")


def test_standard_risk_routes_to_respond():
    graph = _make_graph("Standard")
    result = graph.invoke({"query": "Which sectors are low AML risk?"})
    assert result["aml_risk_flag"] == "Standard"
    assert not result["response"].startswith("[ESCALATED]")
