# 3-Agent Crew: Instructional Workflow Registry
**Implementation Context:** `agent_trio_self_improvement_workflow_definitions`

This directory serves as the **Instructional Engine** for the specialized labor division and self-improvement of the 3-agent crew. It contains the JSON capability blocks consumed by the `LaborDivisionOrchestrator`.

## 📂 Registry Contents

- **01_sdlc_labor_reassignment_v1.json**: The bootstrap instruction set used to provision specialized roles (Dev, QA, Doc) to the agent crew.
- **02_qa_agent_audit_v1.json**: The instructional logic for an autonomous syntax and logic audit across the agent registry.
- **03_doc_agent_synthesis_v1.json**: The synthesis instructions for generating architectural and domain-specific documentation.

## 🚀 Execution Guide

Instructions must be executed from the `reassign_coding_agents_labor_divisions/` directory.

### 🔧 Environment Setup
Ensure the namespace-level environment is active:
```bash
# Relative to this folder:
source ../../.venv/bin/activate
```

## 🤖 Running a Workflow
To trigger an instructional block, pass the relative path of the JSON to the mechanical engine:
bash
# Example: Triggering the Labor 
```bash
python3 orchestrator.py agent_trio_self_improvement_workflow_definitions/01_sdlc_labor_reassignment_v1.json
```
