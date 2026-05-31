# 🤖 Agent Interaction Logs: MCP Agent System

## 📅 Session: 2026-05-19 | Branch: feat/agentic-platform-catalyst
**Agent**: Amazon Q Developer
**Governance Source**: `mcp_agent_system/SKILL.md` (established this session)
**Security Tier**: 3 (Strict Environment Mapping)

### 🎯 High-Level Objective
Connect the two independently mature layers of the repo — the `etl_service` PySpark ETL pipeline and the `mcp_agent_system` LangGraph agent — which were built in parallel across separate commit streams and never wired together. Establish AI-native SDLC governance for the service before proceeding with remaining fixes.

---

### 🛠️ Interaction Trace & Decision Log

#### Round 1: Governance Audit Before Code
- **Intent**: Read `server.py`, `langgraph_aml_agent.py`, `rag_index.py`, `run_demo.py`, `tests/test_langgraph_aml_agent.py`, and `etl_service/src/adapters/spark_companies_builder.py` before writing any code.
- **Findings**:
  - `server.py` `run_aml_agent` handler had hardcoded `sector_rows` with a comment "replace with SparkCompaniesBuilder in prod" — the wire was never connected.
  - `SparkCompaniesBuilder.get_sector_summary()` returns exactly the schema (`sector`, `company_count`, `avg_employees`, `aml_risk_flag`) that `rag_index.build_sector_index()` expects — a `.collect()` call was the entire missing link.
  - `run_demo.py` contained `FINANCEAI PRO™` marketing copy and references to demo files (`ma_advisory_graph_intelligence.py`) that do not exist in `agents/` — dead imports on execution.
  - `_SYSTEM_PROMPT` in `langgraph_aml_agent.py` referenced "Wells Fargo" — a competitor institution.
  - `rag_index.py` uses `OpenAIEmbeddings` with no offline fallback — demo not runnable without `OPENAI_API_KEY`.
- **Result**: Four discrete fixes identified; `SKILL.md` written to encode constraints before any code changes.

#### Round 2: Wire SparkCompaniesBuilder into server.py
- **Intent**: Replace hardcoded `sector_rows` with live data from `SparkCompaniesBuilder.get_sector_summary()`.
- **Decision**: Extracted `_get_sector_rows()` as a module-level helper (not a method) — keeps `FinancialMCPServer` class focused on MCP protocol concerns; Spark lifecycle (create → run → stop) is a one-shot operation that doesn't belong on the server instance.
- **Fallback design**: `try/except Exception` wraps the entire Spark path; on any failure logs a `WARNING` and returns `_FALLBACK_SECTOR_ROWS`. Server never crashes if Spark is unavailable in the agent environment — consistent with the Degraded State contract established in `gpu_ops_alpha_orchestrator`.
- **Fallback data correction**: Original hardcoded rows used `"Finance"` and `"Technology"` — not valid GICS sector names. Corrected to `"Financials"` and `"Information Technology"` to match the Wikipedia CSV source.
- **Scope**: `etl_service` consumed read-only via import — no modifications to the ETL layer (SKILL.md: Scope Contamination guardrail).
- **Result**: `server.py` and `requirements.txt` (`pyspark>=3.5.0` added) committed as `b053734`.

#### Round 3: Establish AI-Native SDLC Governance
- **Intent**: Write `SKILL.md` and open `AGENT_LOGS.md` before proceeding with remaining fixes, so all subsequent work on this branch is logged against the governance layer.
- **Decision**: `SKILL.md` encodes four service-specific constraints not present in `gpu_ops_alpha_orchestrator/SKILL.md`: LLM injection contract, offline-safe contract, system prompt policy, and MCP tool boundary (stub tools must be labeled as such).
- **Result**: `SKILL.md` and `AGENT_LOGS.md` created. Remaining fixes (offline-safe embeddings, system prompt, `run_demo.py` cleanup) to be logged in subsequent rounds.

---

### ⚖️ Architectural Verification (in progress)
- [x] **SparkCompaniesBuilder wire**: `_get_sector_rows()` connects ETL → agent pipeline; fallback ensures server stability
- [x] **Scope isolation**: No modifications to `etl_service/`, `fastapi_backend/`, or `gpu_ops_alpha_orchestrator/`
- [x] **Security**: No raw API keys in source; `OPENAI_API_KEY` consumed only via `os.getenv` in `rag_index.py`
- [ ] **Offline-safe contract**: `FakeEmbeddings` fallback pending
- [ ] **System prompt policy**: "Wells Fargo" reference pending removal
- [ ] **Demo integrity**: `run_demo.py` cleanup pending

#### Round 4: Offline-Safe Contract — FakeEmbeddings Fallback (SKILL.md: Offline-Safe Contract)
- **Intent**: Make the demo runnable without an `OPENAI_API_KEY` — a live API dependency is unacceptable for a demo or CI run.
- **Decision**: Extracted `_embeddings()` factory function in `rag_index.py` gated on `USE_FAKE_EMBEDDINGS=true` env var. Returns `FakeEmbeddings(size=1536)` from `langchain_core.embeddings.fake` (ships with `langchain-core`, no new dependency) when set; falls back to `OpenAIEmbeddings` otherwise.
- **Rejected alternative**: Patching `OpenAIEmbeddings` at the call site — would require callers to know about the mock, violating the injection contract. The env-var gate keeps `build_sector_index()` signature unchanged; callers are unaffected.
- **Size alignment**: `size=1536` matches `text-embedding-3-small` output dimension — FAISS index shape is consistent between fake and real paths.
- **Result**: `rag_index.py` updated; demo runnable offline via `USE_FAKE_EMBEDDINGS=true`.

#### Round 5: System Prompt Policy — Remove Competitor Institution (SKILL.md: System Prompt Policy)
- **Intent**: Remove "Wells Fargo" from `_SYSTEM_PROMPT` in `langgraph_aml_agent.py` per SKILL.md policy.
- **Decision**: Replaced with "a major financial institution" — neutral, domain-accurate, and appropriate for a Morgan Stanley interview artifact.
- **Result**: One-line change; no behavioral impact on graph logic or tests.

---

### ⚖️ Architectural Verification
- [x] **SparkCompaniesBuilder wire**: `_get_sector_rows()` connects ETL → agent pipeline; fallback ensures server stability
- [x] **Scope isolation**: No modifications to `etl_service/`, `fastapi_backend/`, or `gpu_ops_alpha_orchestrator/`
- [x] **Security**: No raw API keys in source; `OPENAI_API_KEY` consumed only via `os.getenv` in `rag_index.py`
- [x] **Offline-safe contract**: `FakeEmbeddings` fallback via `USE_FAKE_EMBEDDINGS=true`
- [x] **System prompt policy**: "Wells Fargo" reference removed
- [x] **Demo integrity**: `run_demo.py` rewritten — single executable path, no dead imports

#### Round 6: Demo Integrity — run_demo.py Rewrite (SKILL.md: Demo Integrity)
- **Intent**: Replace the Nov 2025 showcase launcher with a single executable path that exercises the real pipeline end-to-end.
- **Problems removed**: `FINANCEAI PRO™` marketing copy; interactive menu referencing six demo files that do not exist in `agents/`; hardcoded `sector_rows` with incorrect GICS names; dead `argparse` `--demo aml-agent` branch that duplicated the menu path.
- **Decision**: Single `async main()` that calls `_get_sector_rows()` (the wire connected in Round 2), `build_sector_index()`, `build_aml_graph()`, and `graph.invoke()`. Offline path (`USE_FAKE_EMBEDDINGS=true`) substitutes a `MagicMock` LLM so the full graph executes without any live API call — consistent with the LLM injection contract in `SKILL.md`.
- **Result**: `run_demo.py` reduced from 140 lines to 42. Runnable offline via `USE_FAKE_EMBEDDINGS=true python run_demo.py`.

---

### ⚖️ Architectural Verification
- [x] **SparkCompaniesBuilder wire**: `_get_sector_rows()` connects ETL → agent pipeline; fallback ensures server stability
- [x] **Scope isolation**: No modifications to `etl_service/`, `fastapi_backend/`, or `gpu_ops_alpha_orchestrator/`
- [x] **Security**: No raw API keys in source; `OPENAI_API_KEY` consumed only via `os.getenv` in `rag_index.py`
- [x] **Offline-safe contract**: `FakeEmbeddings` fallback via `USE_FAKE_EMBEDDINGS=true`
- [x] **System prompt policy**: "Wells Fargo" reference removed
- [x] **Demo integrity**: `run_demo.py` rewritten — single executable path, no dead imports

### 🚀 Session Status: GREEN
**Files modified**: `server.py`, `requirements.txt`, `agents/rag_index.py`, `agents/langgraph_aml_agent.py`, `run_demo.py`
**Files created**: `SKILL.md`, `AGENT_LOGS.md`
**Branch**: `feat/agentic-platform-catalyst`

#### Round 7: Testable Spark/ETL Wiring Validation and Commit Prep
- **Intent**: Validate branch health after server Spark dependency refactor and test additions, then prepare PR-ready commit.
- **Test outcome**: `pytest mcp_agent_system/` passed with 13 tests (`test_data_ingestion_agent.py` 8, `test_langgraph_aml_agent.py` 2, `test_server.py` 3).
- **Server refactor documented**:
  - Added `_SparkDependenciesUnavailable` sentinel exception to distinguish missing dependencies from genuine ETL failures.
  - Isolated Spark creation in `_create_spark_session()` and sector extraction in `_load_sector_rows_from_spark()` for independent test seams.
  - Kept `SparkSession` and `SparkCompaniesBuilder` as module-level imports guarded by `ImportError` for injectability/mockability.
- **`test_server.py` contracts covered**:
  - Live path: verifies builder output is returned by `_load_sector_rows_from_spark()`.
  - Fallback path: verifies `_get_sector_rows()` returns fallback rows when Spark dependencies are unavailable.
  - Failure integrity: verifies genuine ETL errors propagate (no silent fallback masking).
- **ETL rename compatibility check**:
  - `etl_service` commit `f2f6fd2` renamed `get_transaction_risk_summary` to `rank_companies_by_sector_headcount`.
  - No impact on MCP server path: `server.py` relies on `SparkCompaniesBuilder.run()` + `get_sector_summary()` only; renamed method is not in the MCP-facing interface contract.
