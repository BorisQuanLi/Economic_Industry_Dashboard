# Superhost API Gateway

A GraphQL microservice demonstrating four production resilience patterns for high-availability data ingestion and external API synchronization. The S&P 500 quarterly filings dataset serves as the domain proxy — the patterns themselves are domain-agnostic.

---

## Architecture

```
GraphQL Client
      │
      ▼
  FastAPI + Strawberry GraphQL
      │
      ├── cache.py      Redis circuit-breaker layer
      ├── db.py         Firestore primary store (async read/write)
      ├── pubsub.py     GCP Pub/Sub dead-letter publisher
      └── models.py     GraphQL type contracts (Entity, Company, FilingRecord)
```

---

## Four Resilience Patterns

### 1. Entity Resolution with Cascading Fallback (`stock_ticker_lookup`)

**Pattern:** Circuit Breaker — Redis → Remote Store → Degraded Response

The `stock_ticker_lookup` query resolves an entity identifier through a three-tier fallback chain:

1. **Redis cache** — sub-millisecond read; returns immediately on hit
2. **Firestore** (`db.py`) — authoritative store; result is back-filled into cache on success
3. **Degraded mode** — if Firestore times out or errors, a safe stub response is returned rather than propagating a 5xx to the caller

This ensures the query never fails hard. Callers receive a valid typed response at every tier; the degradation is observable in the `name` field rather than an HTTP error code.

**Key implementation detail:** The Firestore call is wrapped in `asyncio.wait_for(..., timeout=1.0)` — a hard latency budget that prevents a slow upstream from blocking the event loop.

---

### 2. Idempotent Webhook Sync (`sync_filing`)

**Pattern:** Exactly-Once Delivery via Cache-Keyed Idempotency

Before any external write, `sync_filing` derives a deterministic idempotency key:

```
filing:{ticker}:{aligned_quarter}
```

If that key exists in Redis, the mutation returns immediately without re-posting to the upstream API. This guarantees that duplicate calls — from retries, network replays, or client bugs — produce no side effects.

The idempotency key is only written to cache **after** a confirmed successful sync, so a partial failure cannot mark a filing as synced prematurely.

---

### 3. Temporal Alignment Before Sync (`_calculate_sliding_quarter`)

**Pattern:** Sliding Window Normalization for Cross-Sectional Consistency

Not all data sources report on the same calendar cadence. A naive temporal join conflates records from different economic periods, producing skewed aggregates. The sliding window corrects this before any downstream write:

- Standard filings: calendar quarter derived from filing date
- Outlier cadence (e.g., October fiscal year-end): remapped to the equivalent calendar quarter (`Q4`) so cross-entity comparisons remain valid

This correction is applied **before** the idempotency key is generated, ensuring the cache key reflects the aligned period rather than the raw filing date.

---

### 4. Dead-Letter Queue with Priority Triage (`publish_dead_letter`)

**Pattern:** Sector-Tagged Dead-Letter Queue for Structured Retry

Two failure conditions route to the dead-letter queue rather than returning an error to the caller:

- **Extraordinary filings** (`8-K` report type): escalated immediately for human review, bypassing automated sync entirely
- **Upstream sync failures**: any `httpx` exception during the FMP POST publishes the failed payload to GCP Pub/Sub

Each dead-letter message is tagged with `sector_GICS`, enabling the retry consumer to triage by domain priority (e.g., process Health Care filings before Energy during a sector-specific event) rather than processing failures in arbitrary FIFO order.

The publisher is imported lazily and all exceptions are caught — a Pub/Sub outage degrades to a logged warning rather than cascading into the sync path.

---

## Module Responsibilities

| Module | Responsibility |
|---|---|
| `main.py` | GraphQL schema assembly, resolver logic, resilience orchestration |
| `models.py` | Strawberry type contracts — `Entity`, `Company`, `FilingRecord` |
| `cache.py` | Redis client with graceful degradation; `cache_get` / `cache_set` |
| `db.py` | Firestore async client; `get_company` / `upsert_company` |
| `pubsub.py` | GCP Pub/Sub dead-letter publisher with sector-tagged payloads |

---

## Configuration

| Environment Variable | Default | Purpose |
|---|---|---|
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |
| `CACHE_TTL_SECONDS` | `300` | Cache entry TTL |
| `GCP_PROJECT` | `your-gcp-project` | GCP project for Pub/Sub |
| `DEAD_LETTER_TOPIC` | `filing-dead-letter` | Pub/Sub topic for failed syncs |
| `FMP_API_KEY` | `demo` | Upstream API key |

---

## Running Locally

```bash
cd superhost_api_gateway/
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
# GraphQL playground: http://localhost:8001/graphql
# Health check:       http://localhost:8001/health
```

## Tests

```bash
pytest tests/
```
