---
title: "Tabular Intelligence — AI-Augmented SDLC"
service: "tabular_intelligence"
governance_level: "Security Tier 3"
---

# Tabular Intelligence Policy-as-Code

## 1. Scope

`tabular_intelligence` provides offline-safe statistical testing and XGBoost/Ridge
volatility inference for corporate financial vectors. It must remain isolated
from legacy ETL and multi-agent services.

## 2. Machine-Readable Safety Contract

- `USE_MOCK_ANALYTICS=true` is the default and selects deterministic fixture
  predictions without importing live model binaries.
- `USE_MOCK_ANALYTICS=false` permits XGBoost/Ridge initialization, but requires
  local dependencies and must never load credentials or network state.
- `TabularFeatureVector` and `InferencePrediction` use `extra="forbid"`.
- Feature arrays must be non-empty and rectangular before any statistical or
  model operation.

## 3. Human-in-the-Loop Review Criteria

A change requires explicit human review before merge when it:

1. changes p-value, confidence, significance, or boundary calculations;
2. changes the mock/live execution gate;
3. changes model routing, feature ordering, or target semantics;
4. introduces live data, external credentials, or persistent storage;
5. changes the public contract or demo output schema.

The reviewer must verify the test result, inspect the math boundary, and confirm
that the human decision is recorded in `AGENT_LOGS.md`.

## 4. Execution and Verification Gates

```bash
USE_MOCK_ANALYTICS=true pytest tabular_intelligence/tests/ -v
USE_MOCK_ANALYTICS=true python tabular_intelligence/demo.py
```

The offline demo must complete without network access and emit only validated
`InferencePrediction` records. Live model code is lazy-imported and unreachable
while the mock gate is enabled.

## 5. Governance Artifacts

- `README.md`: Quick Start and execution instructions.
- `AI_AUGMENTED_SDLC.md`: localized Policy-as-Code review policy.
- `AGENT_LOGS.md`: session intent, human intervention, and verification trace.
