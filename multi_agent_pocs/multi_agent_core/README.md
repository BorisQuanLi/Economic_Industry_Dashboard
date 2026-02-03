# Multi-Agent Core Framework
A robust, general-purpose foundation for an enterprise-grade AI-agentic SDLC. 

## Architectural Paradigm
This package implements an **Instructional Engine** approach where general-purpose Python agents in `cli_coding_agents/` consume and execute probabilistic logic defined in the `agent_workflow_definitions/` JSON library.

## Service Components
- **agent_workflow_definitions/**: Capability-based instruction sets (TDD, QA, Documentation).
- **cli_coding_agents/**: Core agent interfaces designed for SDLC task execution.
- **utils/**: Shared cross-cutting concerns and helper modules.

## Deployment
Intended to be executed as a standalone service within the `multi_agent_pocs` namespace.
