import asyncio
import pytest
from unittest.mock import patch, MagicMock
from httpx import AsyncClient, ASGITransport
from main import app, _calculate_sliding_quarter


# ---------------------------------------------------------------------------
# Health & introspection
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "operational"


@pytest.mark.asyncio
async def test_graphql_introspection():
    query = "{ __schema { types { name } } }"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/graphql", json={"query": query})
    assert response.status_code == 200
    assert "data" in response.json()


# ---------------------------------------------------------------------------
# Sliding window (unit — no mocks, no GCP)
# ---------------------------------------------------------------------------

def test_sliding_quarter_apple_october_maps_to_q4():
    """Apple's October filing must align to Q4, not Q3."""
    assert _calculate_sliding_quarter("2024-10-31", "AAPL") == "2024Q4"


def test_sliding_quarter_standard_december_maps_to_q4():
    assert _calculate_sliding_quarter("2024-12-15", "MSFT") == "2024Q4"


def test_sliding_quarter_standard_quarters():
    assert _calculate_sliding_quarter("2024-03-31", "MSFT") == "2024Q1"
    assert _calculate_sliding_quarter("2024-06-30", "MSFT") == "2024Q2"
    assert _calculate_sliding_quarter("2024-09-30", "MSFT") == "2024Q3"


def test_sliding_quarter_non_apple_october_maps_to_q4():
    """October is Q4 for any ticker — only AAPL gets special sliding-window treatment."""
    assert _calculate_sliding_quarter("2024-10-15", "MSFT") == "2024Q4"


# ---------------------------------------------------------------------------
# stock_ticker_lookup — circuit breaker
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_stock_ticker_lookup_cache_hit():
    """Redis cache hit skips Firestore entirely."""
    cached = {
        "id": "AAPL", "ticker": "AAPL", "name": "Apple Inc.",
        "sector_GICS": "Information Technology",
        "is_priority": True, "price_earnings_ratio": 32.5,
    }
    with patch("main.cache_get", return_value=cached):
        query = '{ stockTickerLookup(ticker: "AAPL") { ticker name sectorGics isPriority } }'
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/graphql", json={"query": query})
    data = response.json()["data"]["stockTickerLookup"]
    assert data["ticker"] == "AAPL"
    assert data["isPriority"] is True


@pytest.mark.asyncio
async def test_stock_ticker_lookup_cache_miss_hits_firestore():
    """Cache miss falls through to Firestore and caches the result."""
    with patch("main.cache_get", return_value=None), \
         patch("main.cache_set") as mock_set:
        query = '{ stockTickerLookup(ticker: "AAPL") { ticker isPriority } }'
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/graphql", json={"query": query})
    data = response.json()["data"]["stockTickerLookup"]
    assert data["ticker"] == "AAPL"
    assert data["isPriority"] is True
    mock_set.assert_called_once()


@pytest.mark.asyncio
async def test_stock_ticker_lookup_firestore_timeout_returns_degraded():
    """Firestore timeout falls back to degraded response — service stays responsive."""
    with patch("main.cache_get", return_value=None), \
         patch("main._firestore_lookup", side_effect=asyncio.TimeoutError):
        query = '{ stockTickerLookup(ticker: "AAPL") { ticker name isPriority } }'
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/graphql", json={"query": query})
    data = response.json()["data"]["stockTickerLookup"]
    assert data["name"] == "Degraded Mode"
    assert data["isPriority"] is False


# ---------------------------------------------------------------------------
# sync_filing — webhook + dead-letter
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_sync_filing_idempotent():
    """Already-synced filing is skipped without hitting FMP."""
    with patch("main.cache_get", return_value={"ticker": "AAPL", "aligned_quarter": "2024Q4"}):
        mutation = '''
            mutation {
                syncFiling(input: {ticker: "AAPL", filingDate: "2024-10-31",
                           revenue: 124300000000, sectorGics: "Information Technology"})
            }
        '''
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/graphql", json={"query": mutation})
    assert "Already synced" in response.json()["data"]["syncFiling"]


@pytest.mark.asyncio
async def test_sync_filing_8k_escalates_to_human():
    """Extraordinary 8-K bypasses retry queue and escalates to human review."""
    with patch("main.cache_get", return_value=None), \
         patch("main.publish_dead_letter") as mock_dl:
        mutation = '''
            mutation {
                syncFiling(input: {ticker: "AAPL", filingDate: "2024-10-31",
                           revenue: 0, sectorGics: "Information Technology",
                           reportType: "8-K"})
            }
        '''
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/graphql", json={"query": mutation})
    assert "human review" in response.json()["data"]["syncFiling"]
    mock_dl.assert_called_once()
    # publish_dead_letter(ticker, aligned_quarter, revenue, sector_GICS, reason=...)
    assert mock_dl.call_args.kwargs["reason"] == "Extraordinary 8-K: escalated to human review"


@pytest.mark.asyncio
async def test_sync_filing_successful_fmp_sync():
    """Happy path: FMP responds 200, idempotency key is cached."""
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    with patch("main.cache_get", return_value=None), \
         patch("main.cache_set") as mock_set, \
         patch("httpx.AsyncClient.get", return_value=mock_response):
        mutation = '''
            mutation {
                syncFiling(input: {ticker: "MSFT", filingDate: "2024-12-15",
                           revenue: 69600000000, sectorGics: "Information Technology"})
            }
        '''
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/graphql", json={"query": mutation})
    assert "Synced" in response.json()["data"]["syncFiling"]
    mock_set.assert_called_once()


@pytest.mark.asyncio
async def test_sync_filing_fmp_failure_dead_letters():
    """FMP failure publishes to dead-letter topic with sector_GICS for triage."""
    with patch("main.cache_get", return_value=None), \
         patch("main.publish_dead_letter") as mock_dl, \
         patch("httpx.AsyncClient.get", side_effect=Exception("FMP timeout")):
        mutation = '''
            mutation {
                syncFiling(input: {ticker: "MSFT", filingDate: "2024-12-15",
                           revenue: 69600000000, sectorGics: "Information Technology"})
            }
        '''
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/graphql", json={"query": mutation})
    assert "dead-lettered" in response.json()["data"]["syncFiling"]
    mock_dl.assert_called_once()
    # publish_dead_letter(ticker, aligned_quarter, revenue, sector_GICS, reason)
    assert mock_dl.call_args.args[3] == "Information Technology"


# ---------------------------------------------------------------------------
# cache.py — Redis unavailable graceful degradation (no real Redis needed)
# ---------------------------------------------------------------------------

def test_cache_get_returns_none_when_redis_unavailable():
    from cache import cache_get
    with patch("cache.get_redis", return_value=None):
        assert cache_get("any-key") is None


def test_cache_set_is_noop_when_redis_unavailable():
    from cache import cache_set
    with patch("cache.get_redis", return_value=None):
        cache_set("any-key", {"data": 1})  # must not raise
