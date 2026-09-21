---
name: graph_intelligence
version: 1.0.0
description: >-
  Specialized microservice for private equity relationship intelligence,
  Neo4j graph analytics, and federated query orchestration.
metadata:
  project_id: eid-graph-intelligence
  service_context: graph_analytics
  security_tier: 3
  graph_engine: neo4j-5.x
  storage_target: neo4j-bolt
  owner: boris-dev-ops
---

# 🛡️ Implementation Protocol
- **Offline-Safe Contract**: When `USE_MOCK_GRAPH=true` is set, all graph calls
must return deterministic mock fixtures without requiring an active Neo4j
connection.
- **Ingestion Guardrail**: Ingestion functions (`ingest_ma_edges`,
`ingest_institutional_edges`) must be gated by `RUN_GRAPH_INGESTION=true`
environment variable to prevent unintentional mutations during CI or demo runs.
- **LLM Injection Contract**: Components requiring LLM functionality
(`FederatedQueryLayer`, `run_company_search`) must accept `llm` as an injected
argument rather than instantiating LLM clients inside helper functions.
- **Cross-Service Permission**: Read-only import of
`gpu_ops_alpha_orchestrator.feature_engine.generate_alpha_features` is permitted
for Z-score feature normalization.

# 🚀 Iterative SDLC Workflow
1. **Dependency Sync**: Dependencies are pinned in
`./graph_intelligence/requirements.txt`.
2. **Offline Test Verification**: Execute `python -m pytest
graph_intelligence/tests/ -v` (or via Docker Compose) ensuring zero live Neo4j
or API calls are attempted.
3. **Containerized Demo**: Verify quick-start demo via `docker compose --profile
demo run --rm graph_intelligence`.

# ⚠️ Enterprise Guardrails
- **Scope Contamination**: Do not modify source code in `fastapi_backend/`,
`etl_service/`, or `gpu_ops_alpha_orchestrator/` without explicit cross-service
permission.
- **Secrets Policy**: Secrets (`NEO4J_PASSWORD`, `OPENAI_API_KEY`,
`FMP_API_KEY`) must be read strictly via `os.getenv`.
- **MCP Tool Boundary**: All MCP tool definitions registered in `server.py`
(`find_conflict_paths`, `score_deal_proximity`, `federated_pe_query`) are
labeled as POC.
