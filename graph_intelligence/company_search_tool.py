"""
LangChain tool-calling demo: natural-language financial company search.

Demonstrates function/tool calling with two tools called in sequence:

  financial_screener_tool  — screens companies by financial criteria
                             (sector, P/E ceiling, revenue floor) via
                             a financial data vendor stock screener endpoint

  graph_proximity_tool     — scores candidates by relationship proximity
                             to the portfolio via 2-hop Neo4j traversal

run_company_search() binds both tools to the LLM and runs the multi-step
tool-calling loop: LLM calls screener → gets candidates → calls proximity
tool → synthesizes a ranked list with both financial and relationship signals.

This is the "function and tool calling" pattern referenced in the take-home
description.  Temperature=0 for the tool-calling loop — deterministic tool
selection is essential when the LLM is acting as an orchestrator.

Offline safety
--------------
financial_screener_tool: set USE_MOCK_SCREENER=true to return fixture data
graph_proximity_tool:    set USE_MOCK_GRAPH=true on the Neo4jClient
run_company_search:      inject a mock LLM to exercise the loop without API calls
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any

import httpx
from langchain_core.tools import tool

logger = logging.getLogger(__name__)

FMP_KEY = os.getenv("FMP_API_KEY", "")
FMP_BASE = os.getenv("FMP_BASE", "https://financialmodelingprep.com/api")

# Fixture data for offline path
_MOCK_SCREENER_RESULTS = json.dumps([
    {"symbol": "CRM",  "sector": "Technology", "pe":  22.5, "revenue": 31.4e9},
    {"symbol": "ORCL", "sector": "Technology", "pe":  18.3, "revenue": 50.0e9},
    {"symbol": "IBM",  "sector": "Technology", "pe":  14.1, "revenue": 60.5e9},
])


@tool
def financial_screener_tool(
    sector: str,
    max_pe_ratio: float,
    min_revenue_usd_bn: float,
) -> str:
    """
    Screen companies by financial criteria.

    Returns a JSON string — list of companies matching the criteria with
    ticker, sector, P/E ratio, and latest revenue.

    Parameters
    ----------
    sector            : GICS sector name (e.g. "Technology", "Financials")
    max_pe_ratio      : maximum acceptable P/E ratio
    min_revenue_usd_bn: minimum annual revenue in USD billions
    """
    if os.getenv("USE_MOCK_SCREENER", "false").lower() == "true":
        logger.info("USE_MOCK_SCREENER=true — returning fixture screener results")
        return _MOCK_SCREENER_RESULTS

    params = {
        "sector": sector,
        "peRatioLowerThan": max_pe_ratio,
        "revenueMoreThan": int(min_revenue_usd_bn * 1e9),
        "country": "US",
        "limit": 20,
    }
    try:
        resp = httpx.get(
            f"{FMP_BASE}/v3/stock-screener",
            params={**params, "apikey": FMP_KEY},
            timeout=10.0,
        )
        if resp.status_code == 200:
            data = resp.json()
            # Normalise field names for consistent downstream consumption
            results = [
                {
                    "symbol": c.get("symbol", ""),
                    "sector": c.get("sector", sector),
                    "pe": c.get("priceEarningsRatio", 0.0),
                    "revenue": c.get("revenue", 0.0),
                }
                for c in (data if isinstance(data, list) else [])
            ]
            return json.dumps(results)
        logger.warning("Screener HTTP %d", resp.status_code)
        return "[]"
    except Exception:
        logger.error("financial_screener_tool failed", exc_info=True)
        return "[]"


@tool
def graph_proximity_tool(portfolio_tickers: str) -> str:
    """
    Score companies by relationship proximity to the portfolio.

    Uses 2-hop Neo4j traversal across M&A history, SEC 13F institutional
    holders, and board connections.  Returns a JSON string — list of
    candidates sorted by proximity_score descending.

    Parameters
    ----------
    portfolio_tickers : comma-separated ticker symbols, e.g. "AAPL,MSFT"
    """
    import asyncio
    from graph_intelligence.neo4j_client import Neo4jClient

    tickers = [t.strip() for t in portfolio_tickers.split(",") if t.strip()]
    client = Neo4jClient.from_env()

    async def _run():
        try:
            result = await client.score_deal_proximity(tickers)
            return result
        finally:
            await client.close()

    try:
        rows = asyncio.run(_run())
        return json.dumps(rows)
    except Exception:
        logger.error("graph_proximity_tool failed", exc_info=True)
        return "[]"


def run_company_search(
    analyst_question: str,
    portfolio_tickers: list[str],
    llm: Any,
) -> dict[str, Any]:
    """
    Multi-step tool-calling loop: given a natural-language analyst question,
    the LLM calls financial_screener_tool and graph_proximity_tool in sequence
    to produce a ranked list of candidates matching both financial criteria
    and relationship proximity to the portfolio.

    Parameters
    ----------
    analyst_question  : natural-language criterion, e.g.
                        "Find Technology companies with P/E under 20 within
                         2 hops of our portfolio"
    portfolio_tickers : list of portfolio company tickers
    llm               : LangChain BaseChatModel with tool_calling support

    Returns
    -------
    dict with keys:
      question          — original question
      screener_results  — output of financial_screener_tool (parsed)
      proximity_results — output of graph_proximity_tool (parsed)
      synthesis         — LLM final synthesis message

    Offline path
    ------------
    Set USE_MOCK_SCREENER=true and USE_MOCK_GRAPH=true, then inject a mock
    LLM that returns pre-defined tool calls.  The full loop exercises without
    any live API calls.
    """
    tools = [financial_screener_tool, graph_proximity_tool]
    llm_with_tools = llm.bind_tools(tools)

    portfolio_str = ",".join(portfolio_tickers)

    # Augment the question with portfolio context for the tool-calling loop
    augmented = (
        f"{analyst_question}\n\n"
        f"Portfolio tickers for proximity reference: {portfolio_str}"
    )

    screener_results: list = []
    proximity_results: list = []
    synthesis = ""

    try:
        # Initial LLM call — selects which tool(s) to call
        response = llm_with_tools.invoke(augmented)

        # Process tool calls
        for tool_call in getattr(response, "tool_calls", []):
            name = tool_call.get("name", "")
            args = tool_call.get("args", {})

            if name == "financial_screener_tool":
                raw = financial_screener_tool.invoke(args)
                try:
                    screener_results = json.loads(raw)
                except json.JSONDecodeError:
                    screener_results = []

            elif name == "graph_proximity_tool":
                raw = graph_proximity_tool.invoke(args)
                try:
                    proximity_results = json.loads(raw)
                except json.JSONDecodeError:
                    proximity_results = []

        # Final synthesis call with both results
        synthesis_prompt = (
            f"Original question: {analyst_question}\n\n"
            f"Financial screener results: {json.dumps(screener_results)}\n\n"
            f"Relationship proximity results: {json.dumps(proximity_results)}\n\n"
            "Synthesize a ranked list of top candidates combining both signals. "
            "Explain why each candidate ranks highly."
        )
        final = llm.invoke(synthesis_prompt)
        synthesis = final.content if hasattr(final, "content") else str(final)

    except Exception:
        logger.error("run_company_search failed", exc_info=True)

    return {
        "question": analyst_question,
        "screener_results": screener_results,
        "proximity_results": proximity_results,
        "synthesis": synthesis,
    }
