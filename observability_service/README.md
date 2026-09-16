# Observability Service

## Overview

The `observability_service` is a standalone helper microservice responsible for telemetry, tracing, and evaluation across the multi-service FSI architecture. It provides:

- **Cross-service workflow tracing** — structured Pydantic-schema contracts capturing prompt token counts, tool invocation latency, runtime errors, and end-to-end path tracking.
- **Evaluation framework** — a deterministic protocol for peer services to log validation results and LLM-as-a-judge scoreframes.
- **Offline-safe operation** — all dependencies respect `USE_MOCK_ANALYTICS=true` environment overrides; no live API calls are made during local development or CI.

## Quick Start

### Prerequisites

- Python 3.12 (enforced by CI matrix)
- Virtual environment: `python3 -m venv .venv && source .venv/bin/activate`

### Install

```bash
cd observability_service
pip install -r requirements.txt
```

### Run Tests

```bash
cd observability_service
pytest tests/ -v
```

### Environment Variables

| Variable | Default | Purpose |
|---|---|---|
| `USE_MOCK_ANALYTICS` | `true` | Gate live telemetry off; use fixture data |
| `OBSERVABILITY_LOG_LEVEL` | `INFO` | Logging verbosity for trace ingestion |

## Structure

```
observability_service/
├── README.md              # This file
├── AI_AUGMENTED_SDLC.md   # Human review gates for telemetry & logging
├── AGENT_LOGS.md          # Session trace log
├── requirements.txt       # Python dependencies
├── traces.py              # Pydantic schema contracts & trace engine
├── evals.py               # Evaluation protocol & LLM-as-a-judge scoreframes
└── tests/                 # Test suite (schema boundary, contract validation)
    └── __init__.py
```

## Governance

This service is governed by the root `CLAUDE.md` Service Bootstrapping Policy. All code changes must:

1. Follow conventional commit format: `feat(observability): ...`
2. Pass `ruff` linting before commit.
3. Include unit tests for any new schema fields or validation logic.
4. Respect offline-safe contracts — never hardcode API keys or live endpoints.
