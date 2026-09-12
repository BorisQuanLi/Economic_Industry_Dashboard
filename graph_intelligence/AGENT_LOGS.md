# 📝 Agent Execution Log: `graph_intelligence`

This document records the intent, decision traces, architectural pivots, and verification outcomes for AI agent coding sessions operating on the `graph_intelligence` service.

---

## Session 1: Kiro CLI / Antigravity Agent — Initial Architecture & Implementation (2026-09-11)

### Intent
Implement a private equity graph intelligence microservice featuring Neo4j relationship graph traversal, SEC 13F institutional holder / M&A edge ingestion, RidgeCV deal attractiveness scoring, LLM intent routing over federated data sources (Neo4j + PostgreSQL + FAISS), and multi-source tool-calling search.

### Decision Trace & Architectural Pivots

1. **Round 1 — Codebase Audit & Pattern Discovery**
   - *Audit*: Inspected `gpu_ops_alpha_orchestrator`, `mcp_agent_system`, `etl_service`, and `fastapi_backend`.
   - *Decision*: Adopt the `SKILL.md` + `AGENT_LOGS.md` + `AI_AUGMENTED_SDLC.md` governance triplet from `gpu_ops_alpha_orchestrator`.

2. **Round 2 — Architectural Pivot: Top-Level Microservice**
   - *Initial Draft*: Drafted graph files inside `mcp_agent_system/graph/`.
   - *Pivot*: Promoted graph intelligence to a top-level peer service (`graph_intelligence/`). Graph intelligence represents a distinct domain boundary (PE relationship intelligence) and warrants its own governable service boundary and Docker service profile.

3. **Round 3 — Cross-Service Kernel Reuse**
   - *Discovery*: Identified `gpu_ops_alpha_orchestrator.feature_engine.generate_alpha_features` (rolling Z-score normalization).
   - *Decision*: Import `generate_alpha_features` in `graph_analytics.py` as a read-only dependency to normalize financial multiples and proximity scores before fitting `RidgeCV`. Reuses validated quantitative kernels across service boundaries without code duplication.

4. **Round 4 — DB Connection Pattern Consistency**
   - *Audit*: `etl_service` and `fastapi_backend` use raw `psycopg2` parameterised connections.
   - *Decision*: `build_proximity_feature_matrix` in `graph_analytics.py` accepts a `psycopg2` connection object using `%(tickers)s` tuple filtering, matching existing project patterns.

5. **Round 5 — LLM Router & Tool-Calling Federation**
   - *Design*: Built `FederatedQueryLayer` (`federated_query_layer.py`) using `temperature=0` with Pydantic-validated `RoutingDecision` JSON.
   - *Tool Calling*: Implemented `company_search_tool.py` using LangChain `@tool` decorators for multi-source financial and relationship screening.

6. **Round 6 — Verification & Test Execution**
   - *Outcome*: Executed 16 offline-safe unit tests in Docker container (`docker compose --profile demo run --rm graph_intelligence python -m pytest graph_intelligence/tests/ -v`).
   - *Result*: 16/16 passed in 7.33s.

---

## Session 2: Kiro CLI / Antigravity Agent — NLP Sentiment & Quality Evals Layer (2026-09-11)

### Intent
Extend system capabilities to address text processing and LLM evaluation requirements: implement earnings call transcript ingestion, Pydantic-structured sentiment extraction with LLM-as-a-Judge quality scoring, and quality evaluation benchmarks.

### Decision Trace

1. **Round 7 — Transcript Ingestion & Sectioning**
   - *Implementation*: Added `earnings_transcript_builder.py` in `etl_service/src/adapters/` with sectioning logic separating prepared remarks from Q&A.
   - *Offline Path*: `USE_MOCK_TRANSCRIPTS=true` returns fixture transcript data.

2. **Round 8 — Pydantic Sentiment & LLM-as-a-Judge Evaluation**
   - *Service*: Added `transcript_sentiment_service.py` in `fastapi_backend/services/`.
   - *LLM-as-a-Judge*: Secondary evaluation model (`SentimentJudgeEvaluation`) scores extraction fidelity and reasoning quality.

3. **Round 9 — Quality Evaluation Benchmark Suite & Verification**
   - *Test Suites*: Consolidated test contracts in `graph_intelligence/tests/test_quality_evals.py` and `graph_intelligence/tests/test_transcript_sentiment.py`.
   - *Container Test Verification*: Executed `docker compose --profile demo run --rm graph_intelligence python -m pytest graph_intelligence/tests/ -v`.
   - *Result*: 20 passed, 4 skipped (graceful skip for cross-service imports outside container).

---

### Deliverables Summary
- `graph_intelligence/neo4j_client.py`: Async Neo4j client with `USE_MOCK_GRAPH` offline path.
- `graph_intelligence/graph_builder.py`: Ingestion pipeline with `RUN_GRAPH_INGESTION` safety gate.
- `graph_intelligence/graph_analytics.py`: Feature matrix builder & RidgeCV deal attractiveness scoring.
- `graph_intelligence/federated_query_layer.py`: LLM intent router with Pydantic validation.
- `graph_intelligence/company_search_tool.py`: LangChain multi-source tool-calling agent runner.
- `etl_service/src/adapters/earnings_transcript_builder.py`: Earnings call transcript sectioning adapter.
- `fastapi_backend/services/transcript_sentiment_service.py`: Structured sentiment service with LLM-as-a-Judge evaluation.
- `graph_intelligence/tests/test_quality_evals.py`: Labeled benchmark dataset for intent routing and LangSmith tracing contracts.
- `graph_intelligence/tests/test_transcript_sentiment.py`: Transcript sentiment test suite.

---

## Session 3: Codex CLI — Offline NLP Search Vertical Slice (2026-09-12)

### Intent
Implement the first credential-free vertical slice for the "LLM APIs for
search and NLP" capability. The slice must accept a natural-language analyst
question, validate a closed search intent, retrieve only allowlisted source
records, and return a citation-preserving answer.

### Decision Trace

1. **Feature package boundary**
   - *Decision*: Added `graph_intelligence/nlp_search/` rather than a new
     service or a flat set of service-root modules.
   - *Rationale*: It groups the capability's schemas, injected intent
     extractor, retrieval policy, answer renderer, and orchestrator without
     duplicating the existing federated graph/data adapters.

2. **Human-controlled retrieval boundary**
   - *Decision*: `FinancialSearchIntent` is a closed Pydantic model and has
     typed fields for sector, ticker, P/E, revenue, and relationship signal.
   - *Rationale*: The LLM boundary cannot carry raw SQL, Cypher, or tool names.
     Python applies these fields as allowlisted retrieval predicates. This is
     the first implementation of the human-defined contract that later OpenAI
     and Anthropic adapters must obey.

3. **Offline-first provider seam**
   - *Decision*: Introduced the injected `IntentExtractor` protocol and a
     `FakeIntentExtractor`; did not instantiate a provider SDK in the feature.
   - *Rationale*: CI and the demo run without credentials. A live provider is
     an independently testable adapter that implements the same protocol.

4. **Grounded-answer baseline**
   - *Decision*: First answers are rendered deterministically from retrieved
     records and include record IDs as citations.
   - *Rationale*: This establishes a measurable grounding contract before an
     optional second LLM synthesis pass is allowed.

### Verification

- `test_nlp_search.py`: **4 passed** — grounded records/citations, no-result
  behavior, extra-field rejection, and absent fixture rejection.
- Direct Step 5 demo: printed the hard-coded Technology screen and its three
  `financial:<ticker>` source IDs without credentials.
- Full local graph test run: **26 passed, 2 failed**. The failures pre-date
  this slice and are both `ModuleNotFoundError: sklearn` in existing RidgeCV
  tests; the local virtual environment does not have the dependency pinned in
  `graph_intelligence/requirements.txt` installed.

---

## Session 4: Codex CLI — Package Consolidation and Human Review Gates (2026-09-12)

### Intent
Consolidate existing graph-intelligence modules into domain-oriented packages
while retaining their service boundary, and document the developer review gates
for AI-assisted/LLM-backed changes.

### Decision Trace

1. **Domain-oriented package structure**
   - *Decision*: Move the Neo4j client, ingestion, and analytics modules under
     `graph/`; move federated routing under `federation/`; move the composed
     company-screening workflow under `workflows/`.
   - *Rationale*: These are stable domain boundaries. `demo.py` remains a
     top-level executable entry point, and `nlp_search/` remains the focused
     feature package for structured LLM API search.

2. **Branch scope**
   - *Decision*: Keep `nlp_search` on `feat/graph-relationship-intelligence`.
   - *Rationale*: Its initial retrieval and relationship-signal workflow
     directly composes this service's graph and financial-data contracts. A
     later independent capability such as a reusable vector index or
     evaluation platform should start on its own feature branch.

3. **Human-in-the-loop gates**
   - *Decision*: Record closed intent schemas, application-owned retrieval,
     grounding/citation requirements, offline verification, and developer
     approval of prompts/models/evaluation thresholds in
     `AI_AUGMENTED_SDLC.md`.
   - *Rationale*: An LLM may assist with extraction or synthesis, but cannot
     decide data-access policy, execute generated queries, or self-approve a
     change.
