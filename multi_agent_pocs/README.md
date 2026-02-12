# Multi-Agent Orchestration Service
This directory serves as the namespace for a modular, enterprise-grade AI-agentic SDLC service.

## Architecture
- **multi_agent_core/**: The foundational "Mechanical Engine"—shared registries, polymorphic orchestrator protocols, and instructional TDD framework.
- **reassign_coding_agents_labor_divisions/**: The "Feature" implementation; a specialized 3-agent crew (Dev, QA, Doc) designed to achieve 5x software development productivity through autonomous labor division and SDLC telemetry.

## Design Philosophy
We use a **Mechanical Engine** (Python Orchestrators) driven by an **Instructional Engine** (JSON Capability Blocks) to bridge the gap between low-level capabilities and high-level agentic intent.

## Core Features
- **TDD Governance**: Autonomous workflows (Provisioning, Audit, Synthesis) enforced via `SDLC_BEST_PRACTICES.md`.
- **Specialized V2 Agents**: Role-specific logic for Mistral (Development), Amazon Q (Quality Assurance), and Gemini (Documentation).
- **Telemetry & Reporting**: Automated generation of `QA_AUDIT_REPORT.md` and `TECHNICAL_LANDSCAPE.md` for deep-system visibility.

## Setup & Environment
To ensure service stability, use a single consolidated environment at this root level:
1. **Initialize Venv**: `python3 -m venv .venv && source .venv/bin/activate`
2. **Install Dependencies**: `pip install -r requirements.txt`
