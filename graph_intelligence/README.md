# 🕸️ Graph Intelligence Microservice (`graph_intelligence`)

`graph_intelligence` is a top-level microservice in the Economic & Industry Dashboard ecosystem. It provides private equity relationship intelligence, Neo4j Graph Data Science (GDS) deal proximity scoring, LLM-driven federated intent routing across multi-source databases, and LangChain tool-calling company screening.

---

## 🏗️ Architecture & Component Overview

```
graph_intelligence/
├── SKILL.md                  # Policy-as-Code constraint manifest
├── AGENT_LOGS.md              # Immutable AI agent execution & decision audit log
├── AI_AUGMENTED_SDLC.md      # AI-native development methodology documentation
├── README.md                 # Service overview & quick-start instructions
├── requirements.txt          # Pinned dependencies (neo4j, scikit-learn, langchain-core)
├── Dockerfile                # Container definition (Python 3.12-slim)
├── __init__.py               # Service initialization & exports
├── neo4j_client.py           # Async Neo4j client with USE_MOCK_GRAPH offline path
├── graph_builder.py          # SEC 13F & M&A edge ingestion with RUN_GRAPH_INGESTION guard
├── graph_analytics.py        # Proximity feature matrix + RidgeCV deal attractiveness scoring
├── federated_query_layer.py  # LLM intent router over Neo4j + PostgreSQL + FAISS
├── company_search_tool.py    # LangChain tool-calling (financial screener + graph proximity)
├── demo.py                   # Self-contained quick-start demonstration script
└── tests/
    ├── __init__.py
    └── test_graph_intelligence.py  # 16 offline-safe unit test contracts
```

---

## ⚡ Quick-Start & Execution

### 1. Run Demo Container via Docker Compose

```bash
docker compose --profile demo build graph_intelligence
docker compose --profile demo run --rm graph_intelligence
```

### 2. Run Test Suite via Docker Compose

```bash
docker compose --profile demo run --rm graph_intelligence python -m pytest graph_intelligence/tests/ -v
```

### 3. Local Test Execution (Offline Mode)

```bash
USE_MOCK_GRAPH=true USE_MOCK_SCREENER=true USE_FAKE_EMBEDDINGS=true pytest graph_intelligence/tests/ -v
```

---

## 🛡️ Governance & Safety Guarantees

- **Zero Live Connection Requirement**: By default (`USE_MOCK_GRAPH=true`), all graph client methods return mock fixtures, enabling offline execution and zero-dependency CI runs.
- **Ingestion Safety Gate**: Data ingestion functions require `RUN_GRAPH_INGESTION=true` to prevent unintended graph modifications.
- **Cross-Service Kernel Reuse**: `graph_analytics.py` reuses `generate_alpha_features` from `gpu_ops_alpha_orchestrator` for Z-score feature normalization.
