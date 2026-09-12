# 🤖 AI-Augmented SDLC: Policy-as-Code for `graph_intelligence`

> **Context**: This document details the AI-native development methodology used to build the [`graph_intelligence`](./README.md) microservice — an offline-safe graph analytics and federated query engine.

---

## 1. Overview & Policy-as-Code Governance

The `graph_intelligence` service follows an AI-native governance pattern that prevents architectural drift, credential leakage, and silent failures when using autonomous AI coding agents.

### Core Governance Artifacts

- **[`SKILL.md`](./SKILL.md)**: Machine-readable constraint manifest read by AI agents before writing code. Enforces offline contracts (`USE_MOCK_GRAPH=true`), ingestion safety gates (`RUN_GRAPH_INGESTION=true`), LLM dependency injection contracts, and cross-service read-only permissions.
- **[`AGENT_LOGS.md`](./AGENT_LOGS.md)**: Immutable intent and decision audit trail capturing architectural choices, rejected alternatives, and empirical verification results across sessions.

---

## 2. Verified Governance Outcomes

| Governance Property | Implementation & Verification Evidence |
|---|---|
| **Offline-Safe Contract** | Enforced via `USE_MOCK_GRAPH=true` env default; verified by `TestNeo4jClientMock` (4/4 tests pass with zero live Neo4j connection). |
| **Ingestion Gate** | Ingestion endpoints raise `RuntimeError` unless `RUN_GRAPH_INGESTION=true` is set; verified by `TestNeo4jClientIngestionGate` (2/2 tests pass). |
| **Cross-Service Kernel Reuse** | Reuses `generate_alpha_features` from `gpu_ops_alpha_orchestrator` for Z-score feature normalization in `graph_analytics.py`. |
| **LLM Router Fallback** | `FederatedQueryLayer` gracefully falls back to query all sources on invalid JSON parsing; verified by `TestFederatedQueryLayerRouting` (3/3 tests pass). |
| **Tool Calling Integration** | Multi-source screening demonstrated by `workflows/company_screening.py`; verified by `TestCompanySearchToolMock` (3/3 tests pass). |
| **Human-Controlled NLP Search** | `nlp_search` accepts only closed Pydantic intents; source selection, parameter binding, and citations stay in application code, verified by `test_nlp_search.py`. |

---

## 3. Session Log Summary

| Session | Agent | Key Deliverables | Verification Outcome |
|---|---|---|---|
| 2026-09-11 | Kiro CLI / Antigravity Agent | `neo4j_client.py`, `graph_builder.py`, `graph_analytics.py`, `federated_query_layer.py`, `company_search_tool.py`, `demo.py`, `test_graph_intelligence.py` | 16/16 unit tests passed in Docker container (7.33s) |

Full decision trace: [`AGENT_LOGS.md`](./AGENT_LOGS.md)

---

## 4. Human-in-the-Loop Controls for LLM Features

LLMs are used as constrained components, never as an authority to select
unreviewed data access or change application behavior. The developer defines
and reviews these controls before a provider adapter is enabled:

1. **Closed intent contract.** `nlp_search/schemas.py` forbids extra fields;
   a model cannot pass raw SQL, Cypher, tool names, or source URLs into the
   retrieval layer.
2. **Application-owned retrieval.** Python maps reviewed intent fields to
   allowlisted, parameterized source queries. The model has no database or
   graph credentials and cannot execute a generated query string.
3. **Grounding before generation.** The first vertical slice renders answers
   deterministically from retrieved records and returns source IDs. Any future
   LLM answer synthesizer receives only those records and must preserve their
   citations.
4. **Offline gate before live access.** Fixtures, fake extractors, and unit
   tests must cover the behavior before a live OpenAI or Anthropic adapter is
   activated. Live credentials remain environment variables and are optional
   for CI and demos.
5. **Human review gate.** Changes to schemas, source allowlists, prompts,
   model/parameter choices, or evaluation thresholds require developer review
   and an `AGENT_LOGS.md` decision record. Test and evaluation outcomes, not
   an LLM's self-assessment, determine whether the change proceeds.
