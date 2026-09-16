# AI-Augmented SDLC — Observability Service

## Domain-Specific Human Review Gates

Telemetry and logging involve sensitive operational data. The following human review gates apply to all changes in this service:

### 1. Schema Changes (traces.py)

- **Human review required** for any new Pydantic model field under `TraceSchema`, `ToolInvocationLatency`, or `RuntimeErrorRecord`.
- Verify that `extra="forbid"` is enforced on all trace contract models — this prevents silent schema drift when downstream analytical engines receive new keys.
- New trace categories (e.g., adding a new error type or latency bucket) must be reviewed by a domain engineer before merge.

### 2. Logging Content Policy

- **No PII in traces**: All trace records must strip or hash customer identifiers, company names, or deal-specific data before ingestion.
- **Error message sanitization**: `RuntimeErrorRecord` must not include raw stack traces with file paths or API keys. Review any exception message formatting.
- **Token count accuracy**: Human review required for any change to `prompt_token_count` or `completion_token_count` computation logic — these feed cost-tracking dashboards.

### 3. Evaluation Framework (evals.py)

- **LLM-as-a-judge scoreframes**: Any change to the scoreframe schema or scoring rubric must be reviewed by a quant researcher or AI engineer.
- **Deterministic results**: Eval logging must be reproducible. Random seeds or non-deterministic LLM outputs are prohibited without explicit override flags.
- **Peer service integration**: When a new peer service begins logging eval results, a human must verify that the expected schema is compatible and no data is silently dropped.

### 4. Test Coverage Gate

- **100% schema boundary coverage**: Every Pydantic model must have tests verifying:
  - Accepted fields pass validation.
  - Rejected fields (`extra="forbid"`) raise `ValidationError`.
  - Boundary conditions (null values, zero counts, negative latencies) are handled explicitly.
- Tests must pass with `USE_MOCK_ANALYTICS=true` — no external dependencies.

### 5. Commit Policy

- All commits touching schema or logging logic must include `feat(observability):` prefix.
- Commits that modify error handling or token accounting must reference an `AGENT_LOGS.md` entry.
