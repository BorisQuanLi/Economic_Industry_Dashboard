"""
Test suite for graph_intelligence service.

Offline-safe: all tests run with USE_MOCK_GRAPH=true and USE_MOCK_SCREENER=true.
Zero live API calls, zero live Neo4j or PostgreSQL connections.

Test contracts
--------------
TestNeo4jClientMock
    Verifies the USE_MOCK_GRAPH=true offline path returns fixture data with
    the expected schema.  Does not import neo4j package.

TestNeo4jClientIngestionGate
    Verifies RUN_GRAPH_INGESTION guard raises RuntimeError when not set.

TestGraphAnalyticsMockPath
    Verifies build_proximity_feature_matrix and rank_deals_by_proximity_and_value
    return correctly typed DataFrames on mock fixture.

TestFederatedQueryLayerRouting
    Verifies _route() parses valid JSON into a RoutingDecision, falls back
    gracefully on invalid JSON, and that query() returns the expected top-level
    keys.

TestCompanySearchToolMock
    Verifies financial_screener_tool and graph_proximity_tool return JSON
    strings on mock paths; verifies run_company_search returns the expected
    result dict shape.
"""
from __future__ import annotations

import json
import os
import pytest

# Force offline mode for the entire test module
os.environ.setdefault("USE_MOCK_GRAPH", "true")
os.environ.setdefault("USE_MOCK_SCREENER", "true")
os.environ.setdefault("USE_FAKE_EMBEDDINGS", "true")


# ---------------------------------------------------------------------------
# TestNeo4jClientMock
# ---------------------------------------------------------------------------

class TestNeo4jClientMock:
    def test_from_env_creates_instance(self):
        from graph_intelligence.graph.client import Neo4jClient
        client = Neo4jClient.from_env()
        assert client is not None

    @pytest.mark.asyncio
    async def test_score_deal_proximity_returns_fixture(self):
        from graph_intelligence.graph.client import Neo4jClient
        client = Neo4jClient.from_env()
        rows = await client.score_deal_proximity(["AAPL", "MSFT"])
        assert isinstance(rows, list)
        assert len(rows) > 0
        assert "ticker" in rows[0]
        assert "proximity_score" in rows[0]
        assert "path_type" in rows[0]

    @pytest.mark.asyncio
    async def test_find_conflict_paths_returns_fixture(self):
        from graph_intelligence.graph.client import Neo4jClient
        client = Neo4jClient.from_env()
        paths = await client.find_conflict_paths(
            advisor_ids=["a1"], target_ticker="AAPL"
        )
        assert isinstance(paths, list)
        assert len(paths) > 0
        assert "path" in paths[0]
        assert "path_length" in paths[0]

    @pytest.mark.asyncio
    async def test_close_is_safe_without_driver(self):
        from graph_intelligence.graph.client import Neo4jClient
        client = Neo4jClient.from_env()
        # Should not raise even though driver was never initialised
        await client.close()


# ---------------------------------------------------------------------------
# TestNeo4jClientIngestionGate
# ---------------------------------------------------------------------------

class TestNeo4jClientIngestionGate:
    @pytest.mark.asyncio
    async def test_ingest_ma_edges_raises_without_flag(self):
        from graph_intelligence.graph.client import Neo4jClient
        from graph_intelligence.graph.ingestion import ingest_ma_edges

        os.environ.pop("RUN_GRAPH_INGESTION", None)
        client = Neo4jClient.from_env()
        with pytest.raises(RuntimeError, match="RUN_GRAPH_INGESTION"):
            await ingest_ma_edges(client, tickers=[])

    @pytest.mark.asyncio
    async def test_ingest_institutional_edges_raises_without_flag(self):
        from graph_intelligence.graph.client import Neo4jClient
        from graph_intelligence.graph.ingestion import ingest_institutional_edges

        os.environ.pop("RUN_GRAPH_INGESTION", None)
        client = Neo4jClient.from_env()
        with pytest.raises(RuntimeError, match="RUN_GRAPH_INGESTION"):
            await ingest_institutional_edges(client, tickers=["AAPL"])


# ---------------------------------------------------------------------------
# TestGraphAnalyticsMockPath
# ---------------------------------------------------------------------------

class TestGraphAnalyticsMockPath:
    def test_build_proximity_feature_matrix_returns_dataframe(self):
        from graph_intelligence.graph.analytics import build_proximity_feature_matrix
        df = build_proximity_feature_matrix([], db_conn=None)
        assert len(df) == 3  # mock fixture has 3 rows
        assert "ticker" in df.columns
        assert "proximity_score" in df.columns
        assert "avg_pe_ratio" in df.columns
        assert "latest_revenue_usd_bn" in df.columns

    def test_build_proximity_feature_matrix_sorted_descending(self):
        from graph_intelligence.graph.analytics import build_proximity_feature_matrix
        df = build_proximity_feature_matrix([], db_conn=None)
        scores = df["proximity_score"].tolist()
        assert scores == sorted(scores, reverse=True)

    def test_rank_deals_returns_rank_column(self):
        from graph_intelligence.graph.analytics import (
            build_proximity_feature_matrix,
            rank_deals_by_proximity_and_value,
        )
        df = build_proximity_feature_matrix([], db_conn=None)
        ranked = rank_deals_by_proximity_and_value(df)
        assert "rank" in ranked.columns
        assert "deal_attractiveness_score" in ranked.columns
        assert ranked["rank"].min() == 1

    def test_rank_deals_rank_one_is_highest_score(self):
        from graph_intelligence.graph.analytics import (
            build_proximity_feature_matrix,
            rank_deals_by_proximity_and_value,
        )
        df = build_proximity_feature_matrix([], db_conn=None)
        ranked = rank_deals_by_proximity_and_value(df)
        top = ranked[ranked["rank"] == 1]
        assert top["deal_attractiveness_score"].iloc[0] == ranked["deal_attractiveness_score"].max()


# ---------------------------------------------------------------------------
# TestFederatedQueryLayerRouting
# ---------------------------------------------------------------------------

class TestFederatedQueryLayerRouting:
    def _make_layer(self, llm_content: str):
        from unittest.mock import AsyncMock, MagicMock
        from graph_intelligence.federation.query_layer import FederatedQueryLayer
        from graph_intelligence.graph.client import Neo4jClient

        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(
            return_value=MagicMock(content=llm_content)
        )
        neo4j = Neo4jClient.from_env()
        return FederatedQueryLayer(
            neo4j_client=neo4j,
            db_conn=None,
            faiss_retriever=None,
            llm=mock_llm,
        )

    @pytest.mark.asyncio
    async def test_valid_routing_json_parsed(self):
        routing_json = json.dumps({
            "sources": ["neo4j"],
            "neo4j_query": "deal_proximity",
            "postgres_filter": None,
            "faiss_query": None,
            "rationale": "relationship question",
        })
        layer = self._make_layer(routing_json)
        result = await layer.query("Which companies are near our portfolio?")
        assert "graph" in result
        assert result["routing"]["sources"] == ["neo4j"]

    @pytest.mark.asyncio
    async def test_invalid_json_falls_back_to_all_sources(self):
        layer = self._make_layer("this is not json at all")
        result = await layer.query("Some question")
        # Fallback routes to all three sources
        assert set(result["routing"]["sources"]) == {"neo4j", "postgres", "faiss"}

    @pytest.mark.asyncio
    async def test_result_has_expected_top_level_keys(self):
        routing_json = json.dumps({
            "sources": ["neo4j"],
            "neo4j_query": "deal_proximity",
            "postgres_filter": None,
            "faiss_query": None,
            "rationale": "test",
        })
        layer = self._make_layer(routing_json)
        result = await layer.query("test")
        assert "question" in result
        assert "routing" in result


# ---------------------------------------------------------------------------
# TestCompanySearchToolMock
# ---------------------------------------------------------------------------

class TestCompanySearchToolMock:
    def test_financial_screener_tool_returns_json_string(self):
        from graph_intelligence.workflows.company_screening import financial_screener_tool
        result = financial_screener_tool.invoke({
            "sector": "Technology",
            "max_pe_ratio": 25.0,
            "min_revenue_usd_bn": 20.0,
        })
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert isinstance(parsed, list)
        assert len(parsed) > 0

    def test_graph_proximity_tool_returns_json_string(self):
        from graph_intelligence.workflows.company_screening import graph_proximity_tool
        result = graph_proximity_tool.invoke({"portfolio_tickers": "AAPL,MSFT"})
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert isinstance(parsed, list)

    def test_run_company_search_returns_expected_keys(self):
        from unittest.mock import MagicMock
        from graph_intelligence.workflows.company_screening import run_company_search

        mock_llm = MagicMock()
        # Simulate LLM returning no tool calls (synthesis only path)
        mock_response = MagicMock()
        mock_response.tool_calls = []
        mock_response.content = "Top candidates: CRM (proximity 4, PE 22.5)"
        mock_llm.bind_tools.return_value = mock_llm
        mock_llm.invoke.return_value = mock_response

        result = run_company_search(
            analyst_question="Find Technology companies with P/E under 25",
            portfolio_tickers=["AAPL", "MSFT"],
            llm=mock_llm,
        )
        assert "question" in result
        assert "screener_results" in result
        assert "proximity_results" in result
        assert "synthesis" in result
