# 📊 Tabular Intelligence — ML-powered tabular analytics for financial data

A standalone Python microservice for hypothesis testing and XGBoost/Ridge
volatility inference. It is designed to run fully offline with fixture-backed
analytics and strict Pydantic contracts.

---

## Quick Start & Execution

### 1. Run the Offline Demo

```bash
USE_MOCK_ANALYTICS=true USE_MOCK_GRAPH=true USE_MOCK_SCREENER=true USE_FAKE_EMBEDDINGS=true python tabular_intelligence/demo.py
```

### 2. Run the Local Test Suite

```bash
USE_MOCK_ANALYTICS=true pytest tabular_intelligence/tests/ -v
```

### 3. Run Tests from the Service Directory

```bash
cd tabular_intelligence
USE_MOCK_ANALYTICS=true pytest tests/ -v
```

---

## 📦 Service Layers

| Layer | Responsibilities |
|-------|------------------|
| **contracts** | Pydantic data models, strict schema validation, offline manifest |
| **stats_testing** | Two-sample t-test and one-way ANOVA with offline-safe mocks |
| **xgb_ridge_inference** | XGBoost and Ridge regression with model routing |
| **tests** | Contract, statistical, and inference unit tests |
| **demo** | Interactive end-to-end corporate-vector execution loop |

---

## 🧪 Contracts

`TabularFeatureVector` requires ticker, revenue, EPS, closing price, and
historical volatility arrays. Every array must be non-empty and have the same
length. `InferencePrediction` is a strict output schema with prediction,
confidence, model type, and execution timestamp.

---

## 🛡️ Governance & Safety Guarantees

- **Zero Live Dependency Requirement:** `USE_MOCK_ANALYTICS=true` is the
  default and prevents live XGBoost/Ridge initialization.
- **Human-in-the-Loop Review:** Statistical boundary changes require a logged
  human audit in `AGENT_LOGS.md`.
- **Strict Schema Drift Prevention:** Pydantic uses `extra="forbid"` and
  validates feature matrix dimensions before inference.
- **No Credential Leakage:** The demo and tests use deterministic fixtures only.
