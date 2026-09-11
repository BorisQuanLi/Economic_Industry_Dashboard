"""
Federated query layer demo — three analyst questions, three routing paths.

Demonstrates LLM-driven intent routing across Neo4j + PostgreSQL + FAISS.
Each query exercises a different source:
  Q1 → neo4j    (relationship proximity — M&A history, institutional holders)
  Q2 → postgres (financial fundamentals — revenue, sector)
  Q3 → faiss    (sector risk profile — AML risk, qualitative characteristics)

Run offline (no API keys required):
    USE_MOCK_GRAPH=true USE_FAKE_EMBEDDINGS=true \\
        python -m mcp_agent_system.demos.federated_query_demo

Run with live LLM routing:
    OPENAI_API_KEY=<key> USE_MOCK_GRAPH=true USE_FAKE_EMBEDDINGS=true \\
        python -m mcp_agent_system.demos.federated_query_demo

Note: USE_MOCK_GRAPH=true and USE_FAKE_EMBEDDINGS=true are set here to keep
the data layer offline-safe during the routing demo.  The LLM routing step
itself uses the real OpenAI API when OPENAI_API_KEY is present, or falls back
to a MagicMock when it is not.

LLM parameter judgment demonstrated:
  temperature=0   — routing is classification, not generation; deterministic
                    output ensures the same question routes to the same source
                    across calls
  model=gpt-4o-mini — constrained-output routing task; full gpt-4o reasoning
                    depth not needed; ~15x cheaper per token
"""
import asyncio
import json
import logging
import os

logger = logging.getLogger(__name__)

# Three queries, one per routing path
DEMO_QUERIES = [
    # Routing expectation: neo4j (relationship proximity)
    "Which companies are within 2 hops of our portfolio via "
    "shared institutional holders or M&A history?",

    # Routing expectation: postgres (financial fundamentals)
    "Show me Technology sector companies with revenue above $30 billion.",

    # Routing expectation: faiss (sector risk profile)
    "What is the AML risk profile for the Financials sector?",
]

DEMO_PORTFOLIO = os.getenv("DEMO_PORTFOLIO_TICKERS", "AAPL,MSFT").split(",")


def _build_mock_llm(query: str) -> object:
    """
    Returns a minimal mock LLM that produces a valid routing JSON for the
    given query — used when OPENAI_API_KEY is not set.
    """
    from unittest.mock import AsyncMock, MagicMock

    routing_map = {
        "institutional holders": '{"sources":["neo4j"],"neo4j_query":"deal_proximity","postgres_filter":null,"faiss_query":null,"rationale":"relationship proximity question"}',
        "revenue": '{"sources":["postgres"],"neo4j_query":null,"postgres_filter":"si.sector_gics = \'Information Technology\'","faiss_query":null,"rationale":"financial fundamentals question"}',
        "AML risk": '{"sources":["faiss"],"neo4j_query":null,"postgres_filter":null,"faiss_query":"Financials sector AML risk profile","rationale":"sector risk profile question"}',
    }
    # Pick the first matching key or fall back to all sources
    content = next(
        (v for k, v in routing_map.items() if k.lower() in query.lower()),
        '{"sources":["neo4j","postgres","faiss"],"neo4j_query":"deal_proximity","postgres_filter":null,"faiss_query":"sector risk","rationale":"fallback"}',
    )
    mock = MagicMock()
    mock.ainvoke = AsyncMock(return_value=MagicMock(content=content))
    return mock


async def run_demo() -> None:
    from graph_intelligence.neo4j_client import Neo4jClient
    from graph_intelligence.federated_query_layer import FederatedQueryLayer

    # FAISS retriever — USE_FAKE_EMBEDDINGS path if flag set
    try:
        from mcp_agent_system.agents.rag_index import build_sector_index
        from mcp_agent_system.server import _get_sector_rows
        retriever = build_sector_index(_get_sector_rows()).as_retriever(
            search_kwargs={"k": 1}
        )
    except ImportError:
        retriever = None
        logger.warning("mcp_agent_system not importable — FAISS path will return []")

    # LLM — real if OPENAI_API_KEY present, mock otherwise
    api_key = os.getenv("OPENAI_API_KEY", "")

    neo4j = Neo4jClient.from_env()

    for query in DEMO_QUERIES:
        if api_key:
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        else:
            llm = _build_mock_llm(query)

        layer = FederatedQueryLayer(
            neo4j_client=neo4j,
            db_conn=None,       # PostgreSQL demo path returns [] without conn
            faiss_retriever=retriever,
            llm=llm,
        )

        result = await layer.query(query)

        print(f"\n{'='*60}")
        print(f"Query:   {result['question']}")
        print(f"Routing: {json.dumps(result['routing'], indent=2)}")
        if result.get("graph"):
            print(f"Graph:   {json.dumps(result['graph'], indent=2)}")
        if result.get("financials"):
            print(f"Financials: {result['financials']}")
        if result.get("sector_context"):
            print(f"Sector:  {result['sector_context']}")

    await neo4j.close()
    print(f"\n{'='*60}")
    print("Demo complete.")
    print(
        "Set OPENAI_API_KEY to see live LLM routing decisions. "
        "Set USE_MOCK_GRAPH=false + NEO4J_URI for live graph queries."
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    asyncio.run(run_demo())
