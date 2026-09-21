---
title: "Frontend Dashboard — AI-Augmented SDLC"
service: "frontend"
governance_level: "Standard"
---

# Frontend Policy-as-Code & Review Gates

## 1. Scope
`frontend/` provides the interactive Streamlit presentation tier for the Economic Industry Dashboard, hosting both the core S&P 500 fundamentals visualization and the executive showcases for peer intelligence services (`graph_intelligence`, `tabular_intelligence`, `observability_service`).

## 2. Machine-Readable Safety Contract
- Presentation code must operate offline-safely with fixture fallbacks when backend services or live databases are unreachable.
- No heavy machine learning or graph database binaries (`torch`, `neo4j`, `scipy`) may be added to `frontend/requirements.txt`; showcase components must remain lightweight and decoupled.
- All network requests to backend services must route through `BACKEND_BASE_URL` with graceful exception handling.

## 3. Human-in-the-Loop Review Criteria
A change requires explicit human review before merge when it:
1. Modifies the primary layout, navigation tabs, or analytical charts of the user-facing dashboard;
2. Introduces new network endpoints or changes backend API integration contracts;
3. Modifies the fallback fixture dataset or mock indicators;
4. Impacts containerized execution or port bindings (`8501`).

## 4. Execution and Verification Gates
```bash
# Verify locally or via Docker
docker compose up -d frontend
# Visual verification at http://localhost:8501
```

## 5. Governance Artifacts
- `README.md`: Quick Start and presentation architecture.
- `AI_AUGMENTED_SDLC.md`: Review criteria and safety contracts.
- `AGENT_LOGS.md`: Session intent, human intervention, and verification trace.
