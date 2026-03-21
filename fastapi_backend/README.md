# FastAPI Backend — FinanceAI Pro

Versioned REST API serving S&P 500 sector and company financial analytics to the Streamlit frontend.
Part of the FinanceAI Pro multi-service stack: ETL service → PostgreSQL → **FastAPI backend** → frontend.

## Architecture

```
fastapi_backend/
├── main.py                  # App factory: CORS middleware, router registration
├── settings.py              # Environment config (DB, Redis) via python-dotenv
├── db_session.py            # psycopg2 connection factory; FastAPI Depends() injection
├── cache.py                 # Redis cache-aside layer with graceful degradation
├── routers/
│   ├── sectors.py           # GET /api/v1/sectors/ — sector aggregations (cached)
│   └── analytics.py        # GET /api/v1/analytics/sliding-window
├── services/
│   └── sliding_window.py   # SlidingWindowService — cross-sector alignment logic
├── models/
│   └── financial.py        # Pydantic response models (SlidingWindowAnalytics, CompanyFinancials)
└── tests/
    ├── test_analytics.py
    ├── test_sliding_window_service.py
    └── test_cache.py
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness check |
| GET | `/api/v1/sectors/` | All sectors with quarterly time-series (cached) |
| GET | `/api/v1/sectors/performance/{sector_name}` | Sector performance with sliding window alignment (cached) |
| GET | `/api/v1/sectors/search` | Distinct sector names |
| GET | `/api/v1/sectors/sub-sectors` | All GICS sub-industry names |
| GET | `/api/v1/sectors/companies/{sub_sector_name}/financials` | Company-level quarterly financials |
| GET | `/api/v1/analytics/sliding-window` | Cross-sector aligned analytics |

## Redis Cache Layer

Read-heavy sector aggregation endpoints use a cache-aside pattern backed by Redis.
The service degrades gracefully — if Redis is unavailable, requests fall through to PostgreSQL without error.

```
Request → cache_get(key)
            ├── HIT  → return cached JSON
            └── MISS → query PostgreSQL → cache_set(key, result, ttl) → return result
```

Cache keys follow the scheme `sectors:<resource>:<params>` (e.g. `sectors:all:default`,
`sectors:performance:Technology:revenue`). TTL defaults to 300 seconds, configurable via
`CACHE_TTL_SECONDS`.

## Design Patterns

- **Dependency Injection** — `db_session.get_db_session()` injected via FastAPI `Depends()`;
  connection lifecycle (commit / rollback / close) managed in one place, not in route handlers
- **Service layer** — `SlidingWindowService` encapsulates cross-sector alignment logic,
  independently testable without an HTTP client
- **Pydantic response models** — `SlidingWindowAnalytics`, `CompanyFinancials` enforce
  contract-first API design; serialization errors surface at the boundary, not downstream
- **Versioned routing** — all endpoints under `/api/v1/` prefix; router-per-resource-domain
  (`sectors`, `analytics`) keeps route files focused

## Local Development

```bash
# From fastapi_backend/
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run the API (requires PostgreSQL — see docker-compose.yml at repo root)
uvicorn main:app --reload

# Run tests (no live DB or Redis required — both are mocked)
pytest
```

Interactive docs available at `http://localhost:8000/docs` once the server is running.

## Environment Variables

Copy `.env.example` at the repo root and set:

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | `postgres` | PostgreSQL host |
| `DB_NAME` | `investment_analysis` | Database name |
| `DB_USER` | `postgres` | Database user |
| `DB_PASS` | `postgres` | Database password |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL |
| `CACHE_TTL_SECONDS` | `300` | Cache entry TTL in seconds |

## Running with Docker Compose

```bash
# From repo root — starts FastAPI, ETL service, PostgreSQL, Redis
docker-compose up fastapi_backend
```

## Tests

```
tests/test_analytics.py              — endpoint integration tests via TestClient
tests/test_sliding_window_service.py — service unit tests (async, no HTTP)
tests/test_cache.py                  — cache layer unit tests (Redis mocked)
```

All tests run without a live database or Redis instance.

## Service Context

This service sits between the ETL pipeline and the frontend:

```
etl_service (PySpark + Airflow)
  → PostgreSQL (quarterly_reports, prices_pe, companies, sub_industries)
    → fastapi_backend  ← this service
      → Streamlit frontend
```

The ETL service populates PostgreSQL; this service reads from it and serves
aggregated analytics. The Redis cache layer reduces repeated DB load on
sector-level aggregation queries, which are stable within a trading session.

The cache-aside pattern, service layer separation, and Pydantic contract enforcement are
domain-agnostic — the same architecture applies to any read-heavy aggregation API regardless
of industry.
