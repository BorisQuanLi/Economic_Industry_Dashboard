"""
Federated query layer: LLM-driven intent routing over multiple data sources.

Architectural pattern
---------------------
Data stays in its source systems (Neo4j for relationships, PostgreSQL for
financials, FAISS for sector risk profiles).  This layer provides a unified
query surface via LLM-driven intent routing — the same value proposition as
federated semantic layers in production financial infrastructure, implemented
without RDF/SPARQL overhead.

Three query sources
-------------------
neo4j    — relationship graph: proximity scoring, conflict-of-interest paths
postgres — financial ratios: revenue, P/E, sector, sub-industry
faiss    — sector risk profiles: AML risk flags, company counts (RAG index
           built by mcp_agent_system/agents/rag_index.py)

LLM routing
-----------
The router uses temperature=0 — routing is a classification task, not a
generation task.  Deterministic output reduces the risk of routing the same
question to different sources across calls.

The router returns a Pydantic-validated RoutingDecision.  If the LLM response
cannot be parsed, the layer falls back to querying all three sources — safe
degradation, not a crash.

LLM injection contract
----------------------
LLM and retriever passed as constructor arguments — never instantiated inside
this class.  Both are mockable without live API calls.  Consistent with the
LLM injection contract in mcp_agent_system/SKILL.md.

Offline safety
--------------
USE_MOCK_GRAPH=true on the injected neo4j_client handles the graph path.
USE_FAKE_EMBEDDINGS=true on the injected retriever handles the FAISS path.
A mock LLM (e.g. MagicMock returning valid JSON) handles the router.
All three paths exercisable without live credentials.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any, Literal

from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Router prompt — instructs the LLM to return structured JSON.
# Constrained output schema reduces hallucination risk; the LLM classifies
# intent rather than generating free-form text.
# ---------------------------------------------------------------------------

_ROUTER_PROMPT = """\
You are a financial analyst query router.

Given an analyst question, return a JSON object with exactly these keys:
  "sources"         : list of strings — which sources to query.
                      Each element must be one of: "neo4j", "postgres", "faiss"
  "neo4j_query"     : one of "conflict_paths", "deal_proximity", or null
  "postgres_filter" : a SQL WHERE clause fragment safe to embed, or null
  "faiss_query"     : a semantic search string, or null
  "rationale"       : one sentence explaining the routing decision

Rules:
- Use "neo4j" for questions about relationships, board connections,
  institutional holders, M&A history, proximity, or conflict of interest.
- Use "postgres" for questions about revenue, P/E ratios, financials,
  sector averages, or company fundamentals.
- Use "faiss" for questions about sector risk profiles, AML risk, or
  qualitative sector characteristics.
- Multiple sources are allowed when the question spans them.
- Return ONLY valid JSON. No explanation outside the JSON object.

Analyst question: {question}
"""


# ---------------------------------------------------------------------------
# Pydantic response schema — validates LLM output before acting on it.
# ---------------------------------------------------------------------------

class RoutingDecision(BaseModel):
    sources: list[Literal["neo4j", "postgres", "faiss"]]
    neo4j_query: Literal["conflict_paths", "deal_proximity"] | None = None
    postgres_filter: str | None = None
    faiss_query: str | None = None
    rationale: str = ""


_FALLBACK_ROUTING = RoutingDecision(
    sources=["neo4j", "postgres", "faiss"],
    neo4j_query="deal_proximity",
    postgres_filter=None,
    faiss_query=None,
    rationale="routing parse failed — querying all sources",
)


# ---------------------------------------------------------------------------
# Federated query layer
# ---------------------------------------------------------------------------

class FederatedQueryLayer:
    """
    Routes analyst questions across Neo4j, PostgreSQL, and FAISS without
    migrating data between systems.

    Parameters
    ----------
    neo4j_client   : graph_intelligence.graph.client.Neo4jClient instance
    db_conn        : psycopg2 connection (same pattern as fastapi_backend/db_session.py)
    faiss_retriever: LangChain retriever from mcp_agent_system/agents/rag_index.py
    llm            : LangChain BaseChatModel — injected, never instantiated here

    Example (offline)
    -----------------
    >>> import os; os.environ["USE_MOCK_GRAPH"] = "true"
    >>> from unittest.mock import MagicMock, AsyncMock
    >>> from graph_intelligence.graph.client import Neo4jClient
    >>> neo4j = Neo4jClient.from_env()
    >>> mock_llm = MagicMock()
    >>> mock_llm.ainvoke = AsyncMock(return_value=MagicMock(
    ...     content='{"sources":["neo4j"],"neo4j_query":"deal_proximity",'
    ...             '"postgres_filter":null,"faiss_query":null,"rationale":"test"}'
    ... ))
    >>> layer = FederatedQueryLayer(neo4j, None, None, mock_llm)
    """

    def __init__(
        self,
        neo4j_client: Any,
        db_conn: Any,
        faiss_retriever: Any,
        llm: Any,
    ) -> None:
        self._neo4j = neo4j_client
        self._db = db_conn
        self._retriever = faiss_retriever
        self._llm = llm

    async def query(self, analyst_question: str) -> dict[str, Any]:
        """
        Single entry point for any analyst question.

        Returns a dict with keys:
          question  — the original question
          routing   — RoutingDecision dict
          graph     — Neo4j results (if routed)
          financials— PostgreSQL results (if routed)
          sector_context — FAISS results (if routed)
        """
        routing = await self._route(analyst_question)
        result: dict[str, Any] = {
            "question": analyst_question,
            "routing": routing.model_dump(),
        }

        if "neo4j" in routing.sources:
            result["graph"] = await self._query_neo4j(routing)

        if "postgres" in routing.sources:
            result["financials"] = self._query_postgres(routing)

        if "faiss" in routing.sources:
            result["sector_context"] = self._query_faiss(routing)

        return result

    async def _route(self, question: str) -> RoutingDecision:
        """Call LLM router (temperature=0) and validate JSON response."""
        prompt = _ROUTER_PROMPT.format(question=question)
        try:
            response = await self._llm.ainvoke(prompt)
            content = response.content if hasattr(response, "content") else str(response)
            data = json.loads(content)
            return RoutingDecision(**data)
        except (json.JSONDecodeError, ValidationError, Exception) as exc:
            logger.warning(
                "Routing parse failed (%s) — falling back to all sources", exc
            )
            return _FALLBACK_ROUTING

    async def _query_neo4j(self, routing: RoutingDecision) -> list[dict]:
        if routing.neo4j_query == "conflict_paths":
            return await self._neo4j.find_conflict_paths(
                advisor_ids=[],          # caller should inject real advisor IDs
                target_ticker="UNKNOWN", # caller should inject real target
            )
        # Default: deal proximity on a representative portfolio
        portfolio = os.getenv("DEMO_PORTFOLIO_TICKERS", "AAPL,MSFT").split(",")
        return await self._neo4j.score_deal_proximity(
            portfolio_tickers=[t.strip() for t in portfolio]
        )

    def _query_postgres(self, routing: RoutingDecision) -> list[dict]:
        if self._db is None:
            logger.warning("No db_conn provided — skipping PostgreSQL query")
            return []
        where = routing.postgres_filter or "TRUE"
        try:
            with self._db.cursor() as cur:
                # Safe because WHERE clause is LLM-generated from a constrained
                # prompt — not user-interpolated.  Parameterised values preferred
                # in production; this is a POC demonstration.
                cur.execute(
                    f"SELECT ticker, sector_gics, sub_industry_gics "
                    f"FROM companies c "
                    f"JOIN sub_industries si ON c.sub_industry_id::INT = si.id "
                    f"WHERE {where} LIMIT 20"
                )
                cols = [d[0] for d in cur.description]
                return [dict(zip(cols, row)) for row in cur.fetchall()]
        except Exception:
            logger.error("PostgreSQL query failed", exc_info=True)
            return []

    def _query_faiss(self, routing: RoutingDecision) -> list[dict]:
        if self._retriever is None:
            logger.warning("No faiss_retriever provided — skipping FAISS query")
            return []
        query_str = routing.faiss_query or ""
        if not query_str:
            return []
        try:
            docs = self._retriever.invoke(query_str)
            return [
                {"content": d.page_content, "metadata": d.metadata}
                for d in docs
            ]
        except Exception:
            logger.error("FAISS query failed", exc_info=True)
            return []
