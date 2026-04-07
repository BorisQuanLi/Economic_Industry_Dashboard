# kotlin-data-agent — Kotlin/Ktor GraphQL Agent Service

A JVM backend service written in Kotlin that acts as `agent_006` in the
MCP multi-agent system. It consumes the `fastapi_backend` REST API with
exponential-backoff retry and exposes aggregated S&P 500 sector financial
data over both **GraphQL** and **REST** — introducing a real JVM/HTTP
boundary into an otherwise Python-native agent system.

## Role in the Multi-Agent Architecture

```
MCP Orchestrator (Python)
    │
    ├── agent_001  Data Ingestion      (Python, in-process)
    ├── agent_002  Market Analysis     (Python, in-process)
    ├── agent_003  Risk Assessment     (Python, in-process)
    ├── agent_004  Investment Strategy (Python, in-process)
    └── agent_006  Kotlin Data Agent   ◄── this service, real HTTP boundary
                       │
                       └──► fastapi_backend :8000  /api/v1/sectors/
```

The orchestrator calls `agent_006` via a thin `RemoteKotlinAgent` Python
adapter that implements the same `BaseAgent` interface as the in-process
agents — zero changes to orchestration logic, real network boundary added.
This mirrors the pattern of a Kotlin/JVM service operating alongside
Python ML or data services in a production polyglot architecture.

## Tech Stack

| Concern | Choice |
|---|---|
| Language | Kotlin 2.0 / JVM 17 |
| HTTP server | Ktor 3 (Netty engine) |
| GraphQL | graphql-kotlin-ktor-server 8.3.0 (reflection-based schema) |
| HTTP client | Ktor CIO client with kotlinx.serialization |
| Resilience | Exponential-backoff retry (3 attempts, 100ms base delay) |
| Build | Gradle 8 (Kotlin DSL) |
| Runtime | Docker two-stage build (gradle:8.10-jdk17 → temurin:17-jre-alpine) |

## Endpoints

### `GET /health`
Liveness check. No upstream dependency.

```sh
$ curl -s http://localhost:8090/health
{"status":"healthy","agent_id":"agent_006"}
```

### `POST /graphql`
GraphQL endpoint. Schema is reflection-generated from `SectorQuery` at
startup — no SDL files, no manual type registration. Supports full field
selection.

```sh
$ curl -s -X POST http://localhost:8090/graphql \
    -H "Content-Type: application/json" \
    -d '{"query":"{ sectorReport { recordsProcessed data { sector metrics { performance } } } }"}' \
    | python3 -m json.tool
{
    "data": {
        "sectorReport": {
            "recordsProcessed": 11,
            "data": [
                {"sector": "Industrials",            "metrics": {"performance": 59.4}},
                {"sector": "Financials",             "metrics": {"performance": 60.85}},
                {"sector": "Information Technology", "metrics": {"performance": 58.67}},
                {"sector": "Health Care",            "metrics": {"performance": 62.02}},
                {"sector": "Consumer Discretionary", "metrics": {"performance": 60.57}},
                {"sector": "Consumer Staples",       "metrics": {"performance": 63.53}},
                {"sector": "Real Estate",            "metrics": {"performance": 66.12}},
                {"sector": "Utilities",              "metrics": {"performance": 67.79}},
                {"sector": "Materials",              "metrics": {"performance": 68.35}},
                {"sector": "Communication Services", "metrics": {"performance": 68.45}},
                {"sector": "Energy",                 "metrics": {"performance": 68.84}}
            ]
        }
    }
}
```

### `GET /graphiql`
Interactive GraphiQL IDE — browse the live schema and run queries at
`http://localhost:8090/graphiql`.

### `POST /agent/execute`
REST contract for the MCP orchestrator. Returns the same sector data in
the `SectorReport` envelope the orchestrator expects.

```sh
$ curl -s -X POST http://localhost:8090/agent/execute | python3 -m json.tool
{
    "agentId": "agent_006",
    "status": "SUCCESS",
    "recordsProcessed": 11,
    "validationScore": 0.96,
    "data": [
        {"sector": "Industrials",            "metrics": {"performance": 59.4,  "volatility": 0.0}},
        {"sector": "Financials",             "metrics": {"performance": 60.85, "volatility": 0.0}},
        {"sector": "Information Technology", "metrics": {"performance": 58.67, "volatility": 0.0}}
    ]
}
```

When `fastapi_backend` is unreachable, retry exhausts before returning
`503` with a structured error body — the orchestrator can distinguish a
degraded agent from a crashed one:

```sh
$ curl -s -X POST http://localhost:8090/agent/execute  # upstream down
{"agent_id":"agent_006","status":"ERROR","error":"Connection refused"}
```

## Project Structure

```
kotlin-data-agent/
├── Dockerfile                          # Two-stage: gradle:8.10-jdk17 → temurin:17-jre-alpine
├── build.gradle.kts                    # Ktor 3, graphql-kotlin 8.3, kotlinx.serialization
├── settings.gradle.kts
└── src/
    ├── main/kotlin/com/econdashboard/agent/
    │   ├── Application.kt              # Ktor server — install(GraphQL), routing
    │   ├── agent/AgentController.kt    # POST /agent/execute — MCP orchestrator contract
    │   ├── domain/SectorReport.kt      # DDD value objects: SectorReport, SectorMetrics
    │   ├── graphql/SectorSchema.kt     # GraphQL query resolver: SectorQuery : Query
    │   └── service/FastApiClient.kt    # Ktor CIO client with exponential-backoff retry
    └── test/kotlin/com/econdashboard/agent/service/
        └── RetryTest.kt                # Unit tests: retry on transient failure and exhaustion
```

## Key Design Decisions

**Async coroutines throughout**
Every route handler and service method is `suspend`. The Ktor CIO engine
and `kotlinx.coroutines` handle concurrency without thread-per-request
overhead — the standard model for high-concurrency Kotlin backends.

**Exponential-backoff retry**
`FastApiClient` wraps every upstream call in a `retry(n)` coroutine
helper that delays `100ms * 2^attempt` between attempts. Transient
network errors are absorbed before they surface as client-facing failures.

**GraphQL via reflection-based schema generation**
`graphql-kotlin-ktor-server` reflects over `SectorQuery : Query` at
startup to generate the schema. `install(GraphQL)` at the application
level; `graphQLPostRoute()` registers the endpoint without a lambda —
`graphQLPostRoute` installs its own route-scoped `ContentNegotiation`
internally, so no app-level `ContentNegotiation` is needed and no
`DuplicatePluginException` is triggered.

**DDD value objects**
`SectorReport` and `SectorMetrics` are immutable `@Serializable data class`
value objects. The agent's output contract is expressed in the type system —
breaking changes are caught at compile time.

**Graceful degradation**
`AgentController` wraps the upstream call in `runCatching` and returns
`503 + structured JSON` on failure. Callers can distinguish a degraded
agent from a crashed one without parsing stack traces.

**Two-stage Docker build**
Compiles and packages the fat jar in `gradle:8.10-jdk17`, then copies
only the jar into `eclipse-temurin:17-jre-alpine` (~180MB vs ~600MB for
a full JDK image).

## Quick Start

```sh
# From the repo root — starts the full stack including postgres and fastapi_backend
docker compose up -d kotlin-data-agent

# Liveness check
curl http://localhost:8090/health

# GraphQL — all 11 GICS sectors with field selection
curl -s -X POST http://localhost:8090/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ sectorReport { recordsProcessed data { sector metrics { performance } } } }"}'

# REST agent contract (MCP orchestrator shape)
curl -X POST http://localhost:8090/agent/execute

# Interactive schema explorer
open http://localhost:8090/graphiql
```

## Running Tests Locally

Requires Java 17+ and Gradle 8.x (install via [sdkman](https://sdkman.io)):

```sh
sdk install java 17.0.15-tem
sdk install gradle 8.10.2

cd kotlin-data-agent
gradle test --no-daemon
```

Expected output:
```
BUILD SUCCESSFUL in ~35s
4 actionable tasks: 3 executed, 1 up-to-date
```

## CI/CD

**GitHub Actions** is the canonical pipeline for this repo — a dedicated
`test-kotlin` job (Java 17, Gradle dependency cache) gates the `docker`
integration job alongside the existing Python test matrix. The integration
job builds the full compose stack and health-checks both
`fastapi_backend :8000` and `kotlin-data-agent :8090`.

**Jenkins (local Docker)** mirrors the same pipeline for enterprise CI
simulation. In most corporate environments Jenkins — not GitHub Actions —
is the production pipeline; running it locally in a container keeps that
muscle memory intact and validates that the Gradle build and test steps
are not GitHub-specific.
