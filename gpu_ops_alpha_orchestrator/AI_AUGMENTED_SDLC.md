# 🤖 AI-Augmented SDLC: Policy-as-Code for Autonomous Agents

> **Context**: This document describes the development methodology used to build the [GPU-Ops Alpha Orchestrator](./README.md) — a production-ready ML pipeline for HFT-scale signal processing. The methodology is itself a first-class engineering deliverable.

---

## The Problem: Silent Drift in AI-Assisted Development

As AI coding agents become standard in professional engineering workflows, a new category of operational risk emerges: **behavioral drift** — an agent subtly violating security constraints, exceeding hardware limits, or contaminating service boundaries across sessions, with no traceable decision record.

In elite infrastructure environments (HFT, regulated finance, mission-critical systems), this is unacceptable. The solution implemented here treats AI agent governance the same way mature engineering teams treat infrastructure: as **code**.

---

## The Governance Stack

Two artifacts form the governance layer, both version-controlled alongside the source code they govern:

### [`SKILL.md`](./SKILL.md) — Policy-as-Code

A machine-readable constraint manifest read by every agent at the start of every session. It encodes:

- **Security Tier 3**: All credentials sourced exclusively via `os.getenv`. No hardcoded tokens. Ever.
- **VRAM Hard Cap**: 8 GB threshold enforced structurally (50k-row chunks) and defensively (OOM handler).
- **Fail-Fast Hardware Contract**: CUDA unavailability triggers a defined Degraded State — not a crash, not silent CPU fallback without logging.
- **Scope Boundaries**: Explicit prohibition on modifying `fastapi_backend/` or `etl_service/` without cross-context permission.
- **Dependency Integrity**: New dependencies must be added to `requirements.txt` to trigger CI linting.

No agent can claim ignorance of these constraints — they are re-read before any code is written.

### [`AGENT_LOGS.md`](./AGENT_LOGS.md) — Immutable Audit Trail

A structured "Intent → Decision → Result" log of every architectural decision, rejected alternative, and corrective directive across all agent sessions. This is the git blame for *reasoning*, not just code.

**What gets logged:**
- The intent behind each implementation choice
- Rejected alternatives and why they were rejected
- Human corrective directives (e.g., credential mapping corrections, API compatibility fixes)
- Cross-session knowledge transfer (e.g., the namespace-patching breakthrough carried forward explicitly)

---

## Observed Outcomes Across 4 Agent Sessions

| Governance Property | Evidence |
|---|---|
| Zero credential leakage | Enforced by `SKILL.md` policy + automated test `test_persist_alpha_summary_no_hardcoded_credentials` (scans module source via `inspect.getsource`) |
| Cross-session architectural continuity | Session 3 consumed `astra_builder` without modifying it — adapter contract was logged in Session 1, not re-discovered |
| Namespace-patching knowledge transfer | Session 1's "breakthrough" (patch local module namespace, not source package) explicitly applied in Session 2's TDD suite because it was logged |
| Scope isolation across agents | No unintended modifications to `fastapi_backend/` or `etl_service/` across 3 agents (Kiro-CLI ×2, Amazon Q Developer ×1) |
| Hardware contract compliance | All 18 tests pass on CPU-only WSL2 hardware; GPU benchmark correctly skipped via `@pytest.mark.skipif` — Degraded State contract verified |

---

## Why This Pattern Scales

A single `SKILL.md` + `AGENT_LOGS.md` pair costs minutes to maintain per session. The return:

- **Any agent** (or human engineer) can onboard to the service by reading two files.
- **Any session** can be audited for the reasoning behind any decision without reading the full conversation history.
- **Any constraint violation** is detectable — either by the agent reading policy before acting, or by the automated tests that encode the policy as assertions.

This mirrors how mature engineering organizations use Architecture Decision Records (ADRs) — except here the consumer is both human reviewers *and* AI agents operating autonomously.

---

## Session Log Summary

| Date | Agent | Deliverable | Test Result |
|---|---|---|---|
| 2026-05-02 | Kiro-CLI | Astra vector builder, credential alignment, namespace-patching breakthrough | 3 passed, 1 skipped |
| 2026-05-02 | Amazon Q Developer | `VectorizedSignalProcessor` — 14-day rolling Z-score, OOM fallback, TDD suite | 6 passed, 1 skipped |
| 2026-05-03 | Kiro-CLI | `synthetic_alpha_generator.py` — 1M-tick signal, chunked GPU processing, `.pt` serialization | 13 passed, 1 skipped |
| 2026-05-03 | Kiro-CLI | Astra persistence — statistical fingerprint, `persist_alpha_summary`, Security Tier 3 audit test | 18 passed, 1 skipped |

Full decision trace: [`AGENT_LOGS.md`](./AGENT_LOGS.md)
