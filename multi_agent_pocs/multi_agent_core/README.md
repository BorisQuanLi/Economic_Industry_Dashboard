# Multi-Agent Core Framework
A robust, general-purpose foundation for an enterprise-grade AI-agentic SDLC.

## Architectural Paradigm
This package implements an **Instructional Engine** approach where general-purpose Python agents in `cli_coding_agents/` consume and execute probabilistic logic defined in the `agent_workflow_definitions/` JSON library.

## Core Assets & Service Components
- **models.py**: Shared enterprise communication protocol (AgentTask, AgentResult).
- **orchestrator.py**: Base Class mechanical engine with Registry Discovery and Self-Healing fallbacks.
- **agent_workflow_definitions/**: Capability-based instruction sets (TDD, QA, Documentation).
- **cli_coding_agents/**: Core "Golden Image" agent interfaces.
- **utils/**: Centralized helper modules (File I/O, prompt sanitization).

## Quick Start

### 🔧 Environment Setup
Dependencies are centralized at the namespace root. From the `multi_agent_pocs/` directory:

```bash
python3 -m venv .venv
source ../.venv/bin/activate
pip install -r requirements.txt
```