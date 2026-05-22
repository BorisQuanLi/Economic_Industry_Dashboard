#!/usr/bin/env python3
"""
MCP Agent System — AML Risk Assessment Demo

Runs the LangGraph AML agent end-to-end:
  SparkCompaniesBuilder → FAISS RAG index → ingest → retrieve → reason → (escalate | respond)

Usage:
    python run_demo.py                          # uses SparkCompaniesBuilder (requires Spark)
    USE_FAKE_EMBEDDINGS=true python run_demo.py # offline, no OPENAI_API_KEY required
"""

import asyncio
import json
import os


async def main():
    from mcp_agent_system.server import _get_sector_rows
    from mcp_agent_system.agents.rag_index import build_sector_index
    from mcp_agent_system.agents.langgraph_aml_agent import build_aml_graph

    offline = os.getenv("USE_FAKE_EMBEDDINGS", "").lower() == "true"
    print(f"Embeddings: {'FakeEmbeddings (offline)' if offline else 'OpenAIEmbeddings'}")

    sector_rows = _get_sector_rows()
    print(f"Sectors loaded: {len(sector_rows)}")

    index = build_sector_index(sector_rows)
    retriever = index.as_retriever(search_kwargs={"k": 1})

    if offline:
        from unittest.mock import MagicMock
        llm = MagicMock()
        llm.invoke.return_value = MagicMock(content="[offline mock] AML risk assessment.")
    else:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(model="gpt-4o-mini")

    graph = build_aml_graph(retriever, llm)
    result = graph.invoke({"query": "Which sectors pose the highest AML risk?"})
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
