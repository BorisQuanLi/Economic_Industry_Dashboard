# 🛡️ Economic Industry Dashboard — Repository Architecture & AI Governance Registry

This repository is a multi-service Financial Services Industry (FSI) AI engineering portfolio. Each microservice demonstrates a discrete FSI engineering capability, unified by a shared Policy-as-Code governance pattern (`SKILL.md` + `AGENT_LOGS.md` + `AI_AUGMENTED_SDLC.md`).

---

## 🏛️ Service Map

| Service | Domain | Primary Engineering Capability Demonstrated | Governance Level |
|---|---|---|---|
| [`etl_service/`](./etl_service/) | S&P 500 Fundamentals | PySpark ETL, SQL window analytics, Airflow quota management | Standard |
| [`mcp_agent_system/`](./mcp_agent_system/) | AML Risk Assessment | LangGraph agent, FAISS RAG, Model Context Protocol (MCP) server | Security Tier 3 |
| [`gpu_ops_alpha_orchestrator/`](./gpu_ops_alpha_orchestrator/) | HFT Signal Processing | GPU PyTorch feature engineering, Astra DB vector persistence | Security Tier 3 |
| [`graph_intelligence/`](./graph_intelligence/) | PE Relationship Intelligence | Neo4j GDS, federated LLM query routing, LangChain tool calling | Security Tier 3 |

---

## 🤖 Global AI Agent Session Registry

| Service | Session Date | Agent Model / Interface | Key Deliverables | Verification Outcome |
|---|---|---|---|---|
| `mcp_agent_system/` | 2026-05-21 | Amazon Q Developer | LangGraph AML Agent, PySpark/MCP data flow, FakeEmbeddings fallback | 6/6 tests passed |
| `gpu_ops_alpha_orchestrator/` | 2026-05-02 | Kiro CLI (Anthropic) | Astra vector builder, credential security alignment, namespace patching | 3 passed, 1 skipped |
| `gpu_ops_alpha_orchestrator/` | 2026-05-02 | Amazon Q Developer | `VectorizedSignalProcessor` (14-day rolling Z-score, OOM fallback) | 6 passed, 1 skipped |
| `gpu_ops_alpha_orchestrator/` | 2026-05-03 | Kiro CLI (Anthropic) | `synthetic_alpha_generator.py` (1M-tick signal, GPU chunking) | 13 passed, 1 skipped |
| `gpu_ops_alpha_orchestrator/` | 2026-05-03 | Kiro CLI (Anthropic) | Astra vector persistence & Security Tier 3 credential audit test | 18 passed, 1 skipped |
| `graph_intelligence/` | 2026-09-11 | Kiro CLI / Antigravity Agent | Neo4j client, graph analytics, FederatedQueryLayer, tool calling, 16 unit tests | 16/16 tests passed |

---

## 🔀 Multi-Commit Strategy Rationale

Development on major feature branches (e.g., `feat/graph-relationship-intelligence`) follows a structured multi-commit strategy:
1. **Data Layer Commit**: Core domain client, graph builders, data structures, and statistical analytics.
2. **LLM & Tool-Calling Federation Commit**: Intent routing, multi-source screening tools, and MCP tool endpoints.
3. **Governance & Verification Commit**: Unit tests, Docker orchestration setup, `SKILL.md`, `AGENT_LOGS.md`, `AI_AUGMENTED_SDLC.md`, and service README.

This ensures every commit in the repository git history is clean, logically scoped, and independently reviewable.
