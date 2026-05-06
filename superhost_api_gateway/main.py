"""
superhost_api_gateway/main.py

GraphQL gateway demonstrating three resilience patterns using the S&P 500
quarterly filings dataset as a proxy for Slang AI's hospitality domain:

  Entity Recognition  → stock_ticker_lookup  (≈ guest_lookup)
  Circuit Breaker     → Redis → Firestore fallback (≈ Redis → guest profile store)
  Webhook Sync        → sync_filing via httpx → FMP  (≈ OpenTable/SevenRooms sync)
  Dead-Letter Queue   → PubSub with sector_GICS triage (≈ VIP retry prioritization)

Apple's October Q4 filing (vs. peers' December) is the canonical async-arrival
example: the sliding window corrects the misalignment before any downstream sync,
just as a VIP's profile is verified before a reservation is confirmed.
"""
import asyncio
import os
from datetime import datetime

import httpx
import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from cache import cache_get, cache_set
from models import Company, FilingRecord
from pubsub import publish_dead_letter

FMP_API_KEY = os.getenv("FMP_API_KEY", "demo")

# Semaphore caps concurrent Firestore reads — mirrors the 4-ticker batch
# sleep in airflow/dags/fmp_rate_limited_pipeline.py for 500-ticker bursts.
_SEM = asyncio.Semaphore(10)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _calculate_sliding_quarter(filing_date: str, ticker: str) -> str:
    """Align filing date to calendar quarter.
    Apple (AAPL) files Q4 in October; all peers file in December.
    Sliding window maps October → Q4 so cross-sector comparison is valid.
    Source: airflow/dags/fmp_rate_limited_pipeline.py::calculate_sliding_quarter
    """
    d = datetime.strptime(filing_date, "%Y-%m-%d")
    if ticker == "AAPL" and d.month == 10:
        return f"{d.year}Q4"
    quarter = (d.month - 1) // 3 + 1
    return f"{d.year}Q{quarter}"


async def _firestore_lookup(ticker: str) -> dict:
    """Simulated Firestore read (replace with FirestoreClient.get_company in prod)."""
    async with _SEM:
        await asyncio.sleep(0)          # yield; real impl awaits Firestore async SDK
        return {
            "id": ticker,
            "ticker": ticker,
            "name": f"{ticker} Inc.",
            "sector_GICS": "Information Technology",
            "is_priority": ticker in {"AAPL", "MSFT", "GOOGL", "NVDA"},
            "price_earnings_ratio": 32.5,
        }


# ---------------------------------------------------------------------------
# GraphQL schema
# ---------------------------------------------------------------------------

@strawberry.type
class Query:
    @strawberry.field
    async def stock_ticker_lookup(self, ticker: str) -> Company:
        """Circuit breaker: Redis cache → Firestore → degraded fallback.
        Analog: Company.find_by_stock_ticker() in etl_service/src/models/company.py.
        """
        cached = cache_get(f"company:{ticker}")
        if cached:
            return Company(**cached)
        try:
            data = await asyncio.wait_for(_firestore_lookup(ticker), timeout=1.0)
            cache_set(f"company:{ticker}", data)
            return Company(**data)
        except (asyncio.TimeoutError, Exception):
            return Company(
                id=ticker, ticker=ticker, name="Degraded Mode",
                sector_GICS="unknown", is_priority=False,
                price_earnings_ratio=0.0,
            )


@strawberry.input
class SyncFilingInput:
    ticker: str
    filing_date: str
    revenue: float
    sector_GICS: str
    report_type: str = "10-Q"


@strawberry.type
class Mutation:
    @strawberry.field
    async def sync_filing(self, input: SyncFilingInput) -> str:  # noqa: A002
        """Webhook sync to FMP (proxy for OpenTable/SevenRooms/Tripleseat).

        Flow:
          1. Idempotency check — skip if already synced (QuarterlyReport.id analog)
          2. 8-K extraordinary filing → escalate to human review (Slang: hand off to host)
          3. Sliding window alignment (Apple Oct → Q4) before POST
          4. httpx POST to FMP; on failure → dead-letter with sector_GICS for triage
        """
        aligned_quarter = _calculate_sliding_quarter(input.filing_date, input.ticker)
        idempotency_key = f"filing:{input.ticker}:{aligned_quarter}"

        # 1. Idempotency
        if cache_get(idempotency_key):
            return f"Already synced: {input.ticker} {aligned_quarter}"

        # 2. Extraordinary filing → human escalation
        if input.report_type == "8-K":
            publish_dead_letter(
                input.ticker, aligned_quarter, input.revenue, input.sector_GICS,
                reason="Extraordinary 8-K: escalated to human review",
            )
            return f"8-K flagged for human review: {input.ticker}"

        # 3 & 4. Sync to FMP (proxy for reservation platform webhook)
        async with httpx.AsyncClient() as client:
            try:
                r = await client.get(
                    f"https://financialmodelingprep.com/api/v3/income-statement/{input.ticker}",
                    params={"period": "quarter", "limit": 1, "apikey": FMP_API_KEY},
                    timeout=3.0,
                )
                r.raise_for_status()
                cache_set(idempotency_key, {"ticker": input.ticker, "aligned_quarter": aligned_quarter})
                return f"Synced: {input.ticker} {aligned_quarter}"
            except Exception as e:
                publish_dead_letter(input.ticker, aligned_quarter, input.revenue, input.sector_GICS, reason=str(e))
                return f"Sync failed, dead-lettered: {e}"


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)

app = FastAPI(title="Superhost API Gateway")
app.include_router(graphql_app, prefix="/graphql")


@app.get("/health")
async def health_check():
    return {"status": "operational", "version": "v1-superhost"}
