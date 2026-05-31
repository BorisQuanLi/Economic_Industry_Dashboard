---
name: mcp_agent_system
version: 1.0.0
description: >-
  LangGraph-based AML risk assessment agent exposed over the Model Context Protocol.
  Consumes S&P 500 sector data from SparkCompaniesBuilder and serves the agent graph
  as a callable MCP tool to any MCP-compatible client.
metadata:
  project_id: eid-mcp-agent
  service_context: agentic_platform
  security_tier: 3
  data_source: etl_service.src.adapters.spark_companies_builder.SparkCompaniesBuilder
  vector_store: faiss-cpu (local, no cloud dependency)
  owner: boris-dev-ops
---

# 🛡️ Implementation Protocol

- **LLM Injection Contract**: LLM and retriever must be passed into `build_aml_graph()` as arguments — never instantiated inside graph nodes. Both must be mockable without live API calls.
- **Offline-Safe Contract**: `rag_index.build_sector_index()` must support a `FakeEmbeddings` path gated on `USE_FAKE_EMBEDDINGS=true` env var. The demo must be runnable without an `OPENAI_API_KEY`.
- **Secrets Policy**: `OPENAI_API_KEY` sourced exclusively via `os.getenv`. Agent must scan its own output for raw API keys before finalizing any response.
- **System Prompt Policy**: System prompts must not reference competitor financial institutions by name.

# 🚀 Iterative SDLC Workflow (CI/CD Integrated)

1. **Dependency Sync**: New dependencies added to `mcp_agent_system/requirements.txt` to trigger root-level `ci.yml` linting.
2. **Matrix Alignment**: All Python code must remain compatible with the `3.12` runtime in `.github/workflows/ci.yml`.
3. **Test Coverage**: Agent state transitions (`escalate` vs `respond` routing) must be covered by mocked tests — zero live API calls in the test suite.

# ⚠️ Enterprise Guardrails

- **Scope Contamination**: Never modify `etl_service/`, `fastapi_backend/`, or `gpu_ops_alpha_orchestrator/` without explicit cross-context permission. The one sanctioned exception on this branch: `server.py` imports `SparkCompaniesBuilder` from `etl_service` — read-only consumption, no modifications to the ETL layer.
- **MCP Tool Boundary**: `run_aml_agent` is the only tool in `server.py` that invokes the LangGraph graph. `analyze_sector_performance` and `investment_recommendation` are stub tools — they must be labeled as such and not presented as production implementations.
- **Infrastructure Lock**: Human review mandatory for changes to root `docker-compose.yml` or `.github/workflows/ci.yml` (Security Tier 3 requirement).
- **Demo Integrity**: `run_demo.py` must be runnable end-to-end without dead imports, missing demo files, or marketing copy unrelated to the technical implementation.
