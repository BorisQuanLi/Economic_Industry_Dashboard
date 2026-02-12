# Labor Division Feature: 3-Agent Crew
**Implementation Context:** `reassign_coding_agents_labor_divisions`

This package implements a reorganization of specialized labor division among a crew of three CLI AI coding agents. It serves as a feature-layer implementation driven by the `multi_agent_core` engine.

## 🤖 The Agent Crew
To optimize token consumption and daily budgetary constraints, labor is partitioned across three specialized roles:

*   **Mistral Vibe (The Developer)**: Executes the primary TDD cycle. It transforms natural-language unit tests into Red-Green-Refactor code, manages integration testing, and executes the initial commit strategy.
*   **Amazon Q (The QA Engineer)**: Acts as the secondary auditor. It reviews Developer output to provide refactoring recommendations and quality gates, routing feedback back to Mistral for iteration.
*   **Gemini CLI (The Documentarian)**: Leverages high-context windows to maintain the project's knowledge base. It generates and updates root-level `README.md` and technical `.md` documentation across sub-folders.

## 🏗️ Architectural Paradigm
This package operates on an **Inheritance & Discovery** model:
1.  **Inheritance**: The local `LaborDivisionOrchestrator` inherits from `multi_agent_core.orchestrator.CoreOrchestrator`.
2.  **Registry Discovery**: The orchestrator prioritizes the local `cli_coding_agents/` directory for specialized role logic, falling back to foundational core agents upon detection of corruption or absence.
3.  **Instructional Logic**: Workflow execution is governed by JSON capability blocks.

---

## 🚀 Execution & Demo Flow

### 🔧 Environment Setup
This feature utilizes the centralized environment defined in the `multi_agent_core` foundation. 
From the `multi_agent_pocs/` root:

```bash
source ../.venv/bin/activate
pip install -r ../multi_agent_core/requirements.txt
```

### Framework Sanity Check
Verify that inheritance and framework paths are correctly resolved by running the orchestrator without arguments:
```bash
python3 orchestrator.py
```
