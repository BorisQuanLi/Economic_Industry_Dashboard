---
title: "Next Phase Handover — Re-ranker & Evaluation Layers for graph_intelligence"
service: "graph_intelligence"
branch: "feat/graph-relationship-intelligence"
commit: "150314c"
priority: "Embeddings + Re-rankers (Dr. Lookman must-have skills)"
---

# NEXT_PHASE_HANDOVER.md
Self-contained continuation guide for the `graph_intelligence` microservice.

---

## 1. Current State Baseline

### Git Status
```
## feat/graph-relationship-intelligence...origin/feat/graph-relationship-intelligence [ahead 2]
150314c refactor(graph-intelligence): organize modules by domain
bb7793f feat(nlp-search): add offline grounded search slice
28f3d6b docs(graph): update AGENT_LOGS to document Session 2 decision trace and verification outcomes
13eaf89 docs(evals): quality evaluation benchmark dataset for intent routing and sentiment test suite
...
```

### Test Results (verified)
```
cd /home/boris/software-engineering-projects/refactor-Economic_Industry_Dashboard/Economic_Industry_Dashboard
source .venv/bin/activate
USE_MOCK_GRAPH=true USE_MOCK_SCREENER=true USE_FAKE_EMBEDDINGS=true pytest graph_intelligence/tests/ -v

28 passed in 6.38s
```

### Directory Structure
```
graph_intelligence/
├── SKILL.md                  # Policy-as-Code constraint manifest
├── AGENT_LOGS.md             # Immutable AI agent execution & decision audit log (Sessions 1–4)
├── AI_AUGMENTED_SDLC.md      # AI-native development methodology documentation
├── README.md                 # Service overview & quick-start instructions
├── requirements.txt          # Pinned dependencies (neo4j, scikit-learn, langchain-core, etc.)
├── Dockerfile                # Container definition (Python 3.12-slim)
├── __init__.py
├── demo.py                   # Self-contained quick-start demo (5 steps, fully offline)
├── graph/                    # Neo4j client, ingestion, analytics (RidgeCV, feature matrix)
├── federation/               # FederatedQueryLayer (LLM intent router)
├── nlp_search/               # Closed Pydantic intent contracts, FakeIntentExtractor, parameterized retrieval
├── workflows/                # LangChain tool-calling company screening (financial_screener_tool + graph_proximity_tool)
└── tests/
    ├── __init__.py
    ├── test_graph_intelligence.py  # 16 tests (client, ingestion gate, analytics, routing, company screening)
    ├── test_nlp_search.py          # 4 tests (grounded records, no-result, field rejection, extractor guard)
    ├── test_quality_evals.py       # 3 parametrized + 1 langsmith contract
    └── test_transcript_sentiment.py  # 4 tests (fixture content, sectioning, structured sentiment)
```

### Active venv
- Location: `/home/boris/software-engineering-projects/refactor-Economic_Industry_Dashboard/Economic_Industry_Dashboard/.venv/`
- Activate: `source .venv/bin/activate`
- Key packages installed: neo4j 5.22.0, scikit-learn 1.5.2, langchain-core 0.2.40, openai 1.47.0, pydantic 2.9.2, pytest 8.3.3, pytest-asyncio 0.23.8

---

## 2. Gap Analysis — Rational AI Must-Have Skills

Source: `../refactoring_notes_Economic_Industry_Dashboard/02-resume-n-cover-note/02-use-cases/32-rational-ai-fde-dr-aziz-lookman-shop/00a-must-have-skills-dr-lookman-LinkedIn-post.md`

### ✅ Already Implemented
| Skill | Evidence |
|-------|----------|
| **LLM-as-a-judge** | `test_quality_evals.py` benchmarks + `transcript_sentiment_service.py` |
| **Responses API / structured outputs** | `nlp_search/schemas.py` — Pydantic `model_config = ConfigDict(extra="forbid")`, JSON Schema contracts |
| **Temperature/tool/model selection** | `demo.py` Step 4: `temperature=0` for classification routing; model `gpt-4o-mini` |
| **Tool calling / function calling** | `workflows/company_screening.py`: `bind_tools`, `ll.bind_tools(tools)` |
| **Debugging evals/traces/feedback** | `AGENT_LOGS.md` Session logs + `AI_AUGMENTED_SDLC.md` human-in-the-loop controls |
| **Git, logging, error handling, unit tests** | `SKILL.md` enforcement + pytest suite |

### ❌ Missing — Primary Gap: Embeddings + Re-rankers
| Skill | Missing Component |
|-------|-------------------|
| **Embeddings** | No domain-tuned embedding layer; no vector DB; `USE_FAKE_EMBEDDINGS` is a stub, not implemented |
| **Vector databases for semantic search** | No FAISS index or vector store module |
| **Re-rankers / Implement a re-ranker** | No cross-encoder or LLM re-ranker; ranking is single-pass LLM synthesis only |
| **LLM as re-ranker** | Not implemented |

---

## 3. Architectural Blueprint — Re-ranker + Embeddings Layers

### Proposed New Packages

```
graph_intelligence/
├── embeddings/                       # NEW: Domain-tuned embedding vectors + vector store
│   ├── __init__.py
│   ├── domain_embedder.py            # Loads/computes embeddings; mock fixture path
│   ├── vector_store.py               # FAISS index wrapper; persist/restore pattern
│   ├── contracts.py                  # Pydantic: EmbeddingVector, IndexedDocument
│
├── reranker/                         # NEW: Cross-encoder and LLM-as-re-ranker
│   ├── __init__.py
│   ├── cross_encoder.py              # sentence-transformers cross-encoder (CPU-friendly)
│   ├── llm_reranker.py               # OpenAI Responses API re-ranker (optional, env-gated)
│   ├── contracts.py                  # Pydantic: RankedCandidate, RerankResult
│
├── evals/                            # NEW: Extended evaluation framework
│   ├── __init__.py
│   ├── reranker_evals.py             # NDCG, MRR, precision@k benchmarks
│   ├── embedding_evals.py            # Cluster purity, semantic similarity tests
│   ├── llm_judge_evals.py            # LLM-as-judge reasoning quality assessment
│
└── workflows/                        # (extend)
    ├── company_screening.py          # (existing — add reranker integration)
    ├── ranking_workflow.py           # NEW: Orchestrates nlp_search → reranker → graph enrichment
```

### 3.1. Embeddings Layer — `embeddings/`

**File:** `graph_intelligence/embeddings/domain_embedder.py`

```python
class DomainEmbedder:
    """Produces 768-dimensional embeddings tuned for PE deal criteria.

    Mock path (USE_FAKE_EMBEDDINGS=true):
        Returns deterministic seeded vectors from a small fixture dict.
    Production path:
        Loads sentence-transformers/all-MiniLM-L6-v2 finetuned on
        SEC filings + earnings call transcripts, or calls OpenAI
        text-embedding-3-small when EMBEDDING_API_KEY is set.
    """

    def embed(self, text: str) -> list[float]: ...
    def embed_batch(self, texts: list[str]) -> list[list[float]]: ...
```

**File:** `graph_intelligence/embeddings/vector_store.py`

```python
class FAISSVectorStore:
    """Wraps a FAISS index for fast similarity search.

    Mock path: pre-seeded index with 10 companies.
    Production path: build from embedded company profiles stored in PostgreSQL.
    """

    def query(self, query_vector: list[float], k: int = 10) -> list[IndexedDocument]: ...
    def persist(self, path: str) -> None: ...
    def load(self, path: str) -> None: ...
```

**Contracts:** `graph_intelligence/embeddings/contracts.py`

```python
class IndexedDocument(BaseModel):
    doc_id: str = Field(min_length=1)
    ticker: str
    text: str
    vector: list[float]
    metadata: dict[str, Any]
```

### 3.2. Re-ranker Layer — `reranker/`

**Design Principle:** Accept a list of `RetrievedRecord` + optional graph proximity rows as input; return `RankedCandidate` objects with `rerank_score` and `confidence` fields. Use cross-encoder by default; fall back to LLM-as-reranker (OpenAI) when `OPENAI_API_KEY` is set.

**File:** `graph_intelligence/reranker/cross_encoder.py`

```python
from sentence_transformers import CrossEncoder

class CrossEncoderReranker:
    """Lightweight re-ranker using a cross-encoder model.

    Model: sentence-transformers/ms-marco-MiniLM-L-6-v2
    Input: [query_text, candidate_text] pairs
    Output: relevance score [-1.0, 1.0]
    """

    def rerank(self, question: str, candidates: list[dict]) -> list[RerankResult]:
        # Combine question + candidate text, score with cross-encoder
        ...
```

**File:** `graph_intelligence/reranker/llm_reranker.py`

```python
class LLMReranker:
    """Optional LLM-as-re-ranker using OpenAI Responses API.

    Triggered when OPENAI_API_KEY is set.
    Uses structured output to ensure valid scores.
    """

    def rerank(self, question: str, candidates: list[dict]) -> list[RerankResult]:
        # Call gpt-4o-mini with explicit instruction to score relevance
        # Returns RerankResult objects with scores + rationale
        ...
```

**Contracts:** `graph_intelligence/reranker/contracts.py`

```python
class RerankResult(BaseModel):
    record_id: str
    ticker: str
    rerank_score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str | None = None
    rank: int | None = None
```

### 3.3. Evals Layer — `evals/`

Extend the existing `test_quality_evals.py` pattern:

**File:** `graph_intelligence/evals/reranker_evals.py`

```python
class TestRerankerQualityEvals:
    """Benchmarks reranker improvement over simple relevance sorting."""

    @pytest.mark.parametrize("case", _RERANKER_EVAL_DATASET)
    def test_ndcg_improvement_over_unranked(self, case):
        # Compare DCG of reranked vs. unranked candidate list
        ...

    def test_precision_at_3(self):
        # Assert top-3 candidates match expert-labeled ground truth
        ...
```

---

## 4. Workflow Integration

### Extend `workflows/company_screening.py`

After the current tool-calling loop produces `screener_results` and `proximity_results`, add a reranker step:

```python
# After line 220 — final synthesis call:
from graph_intelligence.reranker.cross_encoder import CrossEncoderReranker

reranker = CrossEncoderReranker()
ranked = reranker.rerank(
    analyst_question,
    candidates=screener_results + proximity_results,
)
# ranked is now a list of RerankResult objects
```

### New file: `workflows/ranking_workflow.py`

```python
"""Orchestrates nlp_search → reranker → graph enrichment for end-to-end ranking."""

class RankingWorkflow:
    def __init__(
        self,
        nlp_service: NlpSearchService,
        reranker: CrossEncoderReranker | LLMReranker,
        neo4j_client: Neo4jClient,
    ) -> None: ...

    async def run(self, question: str, portfolio_tickers: list[str]) -> AnalystAnswer:
        # 1. Extract validated intent from NLP search
        intent_records = self._nlp_search(question)
        # 2. Score relationship proximity via Neo4j GDS
        proximity_rows = await self._graph_proximity(portfolio_tickers)
        # 3. Rerank by combined financial + relationship signal
        ranked = self.reranker.rerank(question, intent_records + proximity_rows)
        # 4. Render grounded answer with citations
        return self._render_answer(question, ranked)
```

### Extend `demo.py` — Add Step 6

```python
def step6_ranking_workflow() -> None:
    """Re-rank company candidates and demonstrate end-to-end quality gain."""
    _header("6 / 6  Re-ranker quality gain  (cross-encoder + LLM judge)")
    # Uses mock embeddings + cross-encoder; prints NDCG before/after
    ...
```

---

## 5. Session Execution Plan

### Session 1 — Embeddings Foundation
```bash
# Activate environment
source .venv/bin/activate
cd graph_intelligence/

# Create embeddings package
touch embeddings/__init__.py embeddings/contracts.py embeddings/domain_embedder.py embeddings/vector_store.py

# Write tests first (TDD)
cat > tests/test_embeddings.py << 'EOF'
def test_mock_embedder_returns_deterministic_vector():
    ...
def test_vector_store_query_returns_top_k():
    ...
EOF

# Run offline
USE_FAKE_EMBEDDINGS=true pytest tests/test_embeddings.py -v
```

### Session 2 — Re-ranker + Initial Evals
```bash
# Create reranker package
mkdir reranker evals
touch reranker/__init__.py reranker/contracts.py reranker/cross_encoder.py reranker/llm_reranker.py
touch evals/__init__.py evals/reranker_evals.py

# Write tests first
cat > tests/test_reranker.py << 'EOF'
def test_cross_encoder_rerank_returns_scores():
    ...
EOF

USE_MOCK_GRAPH=true USE_FAKE_EMBEDDINGS=true pytest tests/test_reranker.py -v
```

### Session 3 — Workflow Integration + Demo
```bash
# Extend company_screening with reranker integration
# Add ranking_workflow.py
# Update demo.py with Step 6
# Run full suite
USE_MOCK_GRAPH=true USE_MOCK_SCREENER=true USE_FAKE_EMBEDDINGS=true pytest tests/ -v
```

---

## 6. Exact Context Commands for Fresh Hermes Session

```bash
# --- Environment Setup ---
cd /home/boris/software-engineering-projects/refactor-Economic_Industry_Dashboard/Economic_Industry_Dashboard
source .venv/bin/activate
export USE_MOCK_GRAPH=true
export USE_MOCK_SCREENER=true
export USE_FAKE_EMBEDDINGS=true
export PYTHONPATH=/home/boris/software-engineering-projects/refactor-Economic_Industry_Dashboard/Economic_Industry_Dashboard

# --- Verify Baseline ---
git status
git log --oneline -3
pytest graph_intelligence/tests/ -v

# --- Read Governance First ---
read_file CLAUDE.md
read_file graph_intelligence/SKILL.md
read_file graph_intelligence/AI_AUGMENTED_SDLC.md
read_file graph_intelligence/AGENT_LOGS.md
read_file graph_intelligence/README.md

# --- Read Existing Code Patterns ---
read_file graph_intelligence/nlp_search/schemas.py
read_file graph_intelligence/nlp_search/service.py
read_file graph_intelligence/nlp_search/intent_extractor.py
read_file graph_intelligence/nlp_search/retrieval.py
read_file graph_intelligence/nlp_search/answer_service.py
read_file graph_intelligence/workflows/company_screening.py
read_file graph_intelligence/tests/test_nlp_search.py
read_file graph_intelligence/tests/test_quality_evals.py
read_file graph_intelligence/demo.py
```

---

## 7. Governance Reminders

- **Offline-safe**: All new modules must default to mock/fixture paths with env-var gates.
- **LLM injection contract**: Re-ranker accepts an injected extractor/reranker, never instantiates providers internally.
- **Human review gate**: Any new prompt, model choice, or evaluation threshold requires an `AGENT_LOGS.md` decision record.
- **No AI co-authorship**: All git commits, docstrings, comments, and documentation are human-authored.
- **Relay-Handoff Protocol**: This feature branch spans multiple distinct AI sessions due to context-window ceilings. If you are finishing a phase but more phases remain, you must update this file's checkpoints, document your new atomic commits, and leave this file intact. Only the final agent completing the last phase is authorized to run git rm NEXT_PHASE_HANDOVER.md.

---

## 8. Key Files Referenced

- `./CLAUDE.md` — Repository-level service map and governance  
- `./graph_intelligence/SKILL.md` — Service-specific constraints  
- `./graph_intelligence/AI_AUGMENTED_SDLC.md` — AI-native development methodology  
- `./graph_intelligence/AGENT_LOGS.md` — Session decision trace  
- `../refactoring_notes_Economic_Industry_Dashboard/02-resume-n-cover-note/02-use-cases/32-rational-ai-fde-dr-aziz-lookman-shop/00-job-description-forward-deployed-engineer.md` — Rational AI FDE job description  
- `../refactoring_notes_Economic_Industry_Dashboard/02-resume-n-cover-note/02-use-cases/32-rational-ai-fde-dr-aziz-lookman-shop/00a-must-have-skills-dr-lookman-LinkedIn-post.md` — Must-have skills list  
- `../refactoring_notes_Economic_Industry_Dashboard/02-resume-n-cover-note/02-use-cases/32-rational-ai-fde-dr-aziz-lookman-shop/11c-codex-cli-response-to-initial-prompt.md` — OpenAI Responses API guidance
