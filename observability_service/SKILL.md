---
name: observability_service
version: 1.0.0
description: >-
  Telemetry and evaluation contracts for cross-service workflow observability.
metadata:
  project_id: eid-observability-service
  service_context: telemetry_evaluation
  security_tier: 3
  owner: boris-dev-ops
---

# SKILL.md — Observability Service Telemetry Engine

## Purpose
Maintain the strict Pydantic telemetry layer for cross-service workflow
tracking.

## Procedures

### Adding / Editing Trace Contracts (traces.py)
1. Open `observability_service/traces.py`.
2. Add fields only to `TracePayload`; enforce `extra="forbid"` in
`model_config`.
3. Use `Field(..., ge=0)` for counts and `Dict[str, float]` for latencies.
4. Never remove existing fields without updating `tests/test_observability.py`.

### Running Tests
- Local (if venv has pydantic): `pytest observability_service/tests/ -v`
- Container (guaranteed): `docker build -t observability_service:test -f
observability_service/Dockerfile .`
- Demo profile: `docker compose --profile demo build observability_service` per
root `CLAUDE.md`.

### Expanding the Service
- Add new peer-service trace ingestion by updating `main.py` validation checks.
- Log session changes in `AGENT_LOGS.md`; use `feat(observability):` commit
prefix.
