"""
graph_intelligence quick-start demo.

Runs entirely within this package — no cross-service imports required.
Demonstrates all four core capabilities offline:

  1. Deal proximity scoring  — Neo4j 2-hop traversal (mock fixture)
  2. Proximity feature matrix — SQL join pattern + pandas merge (mock fixture)
  3. RidgeCV deal ranking    — cross-validated regularised regression on features
  4. Federated query routing  — LLM intent routing across Neo4j / PostgreSQL / FAISS

Run via Docker (no credentials required):
    docker compose --profile demo up graph_intelligence

Run locally (requires graph_intelligence dependencies installed):
    USE_MOCK_GRAPH=true python demo.py

Set OPENAI_API_KEY to see live LLM routing decisions in step 4.
Set USE_MOCK_GRAPH=false + NEO4J_URI to run steps 1-3 against a live graph.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any

logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s %(message)s")

os.environ.setdefault("USE_MOCK_GRAPH", "true")
os.environ.setdefault("USE_MOCK_SCREENER", "true")

PORTFOLIO = ["AAPL", "MSFT"]
SEP = "=" * 64


def _header(title: str) -> None:
    print(f"\n{SEP}\n  {title}\n{SEP}")


# ---------------------------------------------------------------------------
# Step 1 — proximity scoring
# ---------------------------------------------------------------------------

async def step1_proximity() -> list[dict]:
    _header("1 / 4  Deal proximity scoring  (Neo4j 2-hop traversal)")
    from graph_intelligence.neo4j_client import Neo4jClient
    client = Neo4jClient.from_env()
    rows = await client.score_deal_proximity(PORTFOLIO)
    await client.close()
    print(f"Portfolio: {PORTFOLIO}")
    print(f"Candidates within 2 hops  ({len(rows)} found):")
    for r in rows:
        print(f"  {r['ticker']:6s}  proximity={r['proximity_score']}  via {r['path_type']}")
    return rows


# ---------------------------------------------------------------------------
# Step 2 — feature matrix
# ---------------------------------------------------------------------------

def step2_feature_matrix(proximity_rows: list[dict]) -> Any:
    _header("2 / 4  Proximity feature matrix  (SQL join pattern + pandas merge)")
    from graph_intelligence.graph_analytics import build_proximity_feature_matrix
    df = build_proximity_feature_matrix(proximity_rows, db_conn=None)
    print("Columns:", list(df.columns))
    print(
        df[["ticker", "proximity_score", "avg_pe_ratio", "latest_revenue_usd_bn"]]
        .to_string(index=False)
    )
    return df


# ---------------------------------------------------------------------------
# Step 3 — RidgeCV ranking
# ---------------------------------------------------------------------------

def step3_ranking(df: Any) -> None:
    _header("3 / 4  RidgeCV deal attractiveness ranking")
    from graph_intelligence.graph_analytics import rank_deals_by_proximity_and_value
    ranked = rank_deals_by_proximity_and_value(df)
    print("Ranked candidates  (rank 1 = most attractive):")
    print(
        ranked[["rank", "ticker", "deal_attractiveness_score",
                "proximity_score", "avg_pe_ratio"]]
        .to_string(index=False)
    )
    print(
        "\nNote: label is synthetic — demonstrates RidgeCV pipeline, "
        "not a calibrated production model."
    )


# ---------------------------------------------------------------------------
# Step 4 — federated routing
# ---------------------------------------------------------------------------

_ROUTING_MAP = {
    "institutional holders": {
        "sources": ["neo4j"], "neo4j_query": "deal_proximity",
        "postgres_filter": None, "faiss_query": None,
        "rationale": "relationship proximity question — route to Neo4j",
    },
    "revenue": {
        "sources": ["postgres"], "neo4j_query": None,
        "postgres_filter": "si.sector_gics = 'Information Technology'",
        "faiss_query": None,
        "rationale": "financial fundamentals question — route to PostgreSQL",
    },
    "aml risk": {
        "sources": ["faiss"], "neo4j_query": None,
        "postgres_filter": None, "faiss_query": "Financials sector AML risk",
        "rationale": "sector risk profile question — route to FAISS",
    },
}

DEMO_QUERIES = [
    "Which companies are within 2 hops of our portfolio via shared institutional holders?",
    "Show me Technology sector companies with revenue above $30 billion.",
    "What is the AML risk profile for the Financials sector?",
]


async def step4_federated_routing() -> None:
    _header("4 / 4  Federated query routing  (LLM intent router, temperature=0)")
    from unittest.mock import AsyncMock, MagicMock

    from graph_intelligence.neo4j_client import Neo4jClient
    from graph_intelligence.federated_query_layer import FederatedQueryLayer

    api_key = os.getenv("OPENAI_API_KEY", "")
    neo4j = Neo4jClient.from_env()

    for query in DEMO_QUERIES:
        if api_key:
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            label = "live LLM (gpt-4o-mini, temp=0)"
        else:
            routing = next(
                (v for k, v in _ROUTING_MAP.items() if k in query.lower()),
                {
                    "sources": ["neo4j", "postgres", "faiss"],
                    "neo4j_query": "deal_proximity",
                    "postgres_filter": None, "faiss_query": None,
                    "rationale": "fallback — all sources",
                },
            )
            mock = MagicMock()
            mock.ainvoke = AsyncMock(
                return_value=MagicMock(content=json.dumps(routing))
            )
            llm = mock
            label = "mock LLM"

        layer = FederatedQueryLayer(
            neo4j_client=neo4j,
            db_conn=None,
            faiss_retriever=None,
            llm=llm,
        )
        result = await layer.query(query)
        r = result["routing"]

        print(f"\nQuery [{label}]:")
        print(f"  {query}")
        print(f"  → sources:   {r['sources']}")
        print(f"  → rationale: {r.get('rationale', '')}")
        if result.get("graph"):
            print(f"  → graph rows returned: {len(result['graph'])}")

    await neo4j.close()

    if not api_key:
        print("\nTip: set OPENAI_API_KEY to see live LLM routing decisions.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main() -> None:
    print(f"\n{SEP}")
    print("  graph_intelligence  —  quick-start demo")
    print(f"  USE_MOCK_GRAPH  = {os.getenv('USE_MOCK_GRAPH', 'true')}")
    print(f"  OPENAI_API_KEY  = {'set' if os.getenv('OPENAI_API_KEY') else 'not set  (mock LLM for step 4)'}")
    print(SEP)

    proximity_rows = await step1_proximity()
    df = step2_feature_matrix(proximity_rows)
    step3_ranking(df)
    await step4_federated_routing()

    print(f"\n{SEP}")
    print("  Demo complete.")
    print(f"{SEP}\n")


if __name__ == "__main__":
    asyncio.run(main())
