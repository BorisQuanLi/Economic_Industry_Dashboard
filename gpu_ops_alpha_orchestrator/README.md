# 🚀 GPU-Ops Alpha Orchestrator (EID-MW Integration)

## 🎯 Design Philosophy
This microservice is the **Operational Alpha** layer for the Economic Industry Dashboard (EID). It bridges **Quantitative Research** and **Platform Engineering** by automating the transition from raw macroeconomic datasets to GPU-accelerated signal generation and cloud-native vector persistence.

Adopting a **"Data-First" architecture**, the service prioritizes the precision of automated feature engineering over model complexity — features, not architecture, drive measurable alpha.

---

## 🤖 AI-Augmented SDLC

This service was built using a structured **AI-Native SDLC** where multiple AI coding agents (Kiro-CLI, Amazon Q Developer) operate under machine-readable governance constraints — not ad-hoc prompting.

| Artifact | Role |
|---|---|
| [`SKILL.md`](./SKILL.md) | Policy-as-Code — Security Tier 3, 8 GB VRAM cap, Fail-Fast contract, scope boundaries. Re-read by every agent before every session. |
| [`AGENT_LOGS.md`](./AGENT_LOGS.md) | Immutable audit trail — "Intent → Decision → Result" log across all agent sessions. The git blame for *reasoning*, not just code. |

Zero credential leakage, full scope isolation, and cross-session architectural continuity across 4 sessions and 3 agents — all verified by the test suite.

📄 **Full methodology writeup**: [AI_AUGMENTED_SDLC.md](./AI_AUGMENTED_SDLC.md)

---

## 🏗️ MVP: Implemented Pipeline

The MVP delivers a complete, end-to-end signal processing pipeline across three stages:

```text
generate_signal()          →   [1M, 64] tensor (Gaussian noise + sine drift)
        │
        ▼
process_in_chunks()        →   generate_alpha_features() per 50k-row chunk
        │                      (Z-score normalization, CUDA or CPU fallback)
        ▼
gpu_cache/alpha_signals.pt →   zero-copy .pt handoff
        │
        ▼
generate_signal_summary()  →   statistical fingerprint {mean, std, max_variance}
        │                      (computed on CPU — no VRAM held during I/O)
        ▼
persist_alpha_summary()    →   Astra DB alpha_signals collection
                               ($vectorize → NVIDIA nv-embedqa-e5-v5 on GCP H100)
```

### Modules

| File | Role |
|---|---|
| `feature_engine.py` | `VectorizedSignalProcessor` — 14-day rolling Z-score via `torch.unfold`; `generate_alpha_features()` — cross-feature normalization kernel |
| `synthetic_alpha_generator.py` | 1M-tick signal generation, chunked GPU processing, statistical fingerprinting, Astra persistence |

### Run the full pipeline
```bash
cd gpu_ops_alpha_orchestrator/
python3 synthetic_alpha_generator.py
```
Output:
```
Alpha signals written to gpu_cache/alpha_signals.pt  shape=torch.Size([1000000, 64])
Statistical fingerprint: {'mean': ..., 'std': ..., 'max_variance': ...}
Summary persisted to Astra alpha_signals collection.
```

---

## 🛡️ Operational Reliability & Resource Governance

**Memory Management (SKILL.md: 8 GB VRAM hard cap)**
- Signal processed in 50k-row chunks (≈ 12.8 MB each) — structurally enforces the VRAM threshold.
- `torch.cuda.OutOfMemoryError` caught per chunk: `empty_cache()` called, chunk retried on CPU.
- Statistical fingerprint computed via `.cpu()` before reductions — no VRAM held during Astra I/O.

**Degraded State**
- `torch.device("cuda" if available else "cpu")` resolved at init time in `VectorizedSignalProcessor`.
- All pipeline stages complete on CPU-only hardware (WSL2, CI runners) without modification.
- Astra `_collection is None` → silent no-op with `WARNING` log; pipeline does not crash.

**Security Tier 3**
- `ASTRA_DB_TOKEN` and `ASTRA_DB_API_ENDPOINT` sourced exclusively via `os.getenv`.
- Zero raw credentials in source — enforced by automated test (`test_persist_alpha_summary_no_hardcoded_credentials`).

---

## 🧪 Test Suite

```bash
pytest gpu_ops_alpha_orchestrator/ -v
# 18 passed, 1 skipped (GPU benchmark — no CUDA device, correct Degraded State behavior)
```

| Test file | Coverage |
|---|---|
| `test_feature_engine.py` | Shape, stationarity, known-value Z-score, CPU output, OOM fallback, GPU benchmark |
| `test_signal_scale.py` | Degraded state, signal shape/drift, serialization, 1M vs 1k latency benchmark, summary correctness, Astra delegation, credential scan |
| `test_imports.py` | Module import smoke test |

---

## 🏛️ Infrastructure

- **Compute**: CUDA-accelerated PyTorch kernels; CPU fallback on non-GPU hardware.
- **Storage**: `gpu_cache/alpha_signals.pt` for zero-copy tensor handoff; Astra DB (GCP us-east1) for vector persistence.
- **Embedding**: NVIDIA `nv-embedqa-e5-v5` via Astra `$vectorize` — offloads to GCP H100 fabric, preserving local VRAM for feature computation.
- **Orchestration**: Docker Compose with NVIDIA Container Toolkit reservations; Kubernetes-ready.

### Environment variables
```bash
ASTRA_DB_TOKEN=<from astra.datastax.com>
ASTRA_DB_API_ENDPOINT=<GCP us-east1 database URL>
ASTRA_DB_KEYSPACE=alpha_signals   # default
```

### Containerized deployment
```bash
docker compose up -d gpu-ops-alpha-orchestrator
curl http://localhost:8070/health/gpu-status
```

> **Note on non-GPU hardware**: `health/gpu-status` returns `critical_failure` by design — the Fail-Fast contract protects pipeline latency requirements. All compute stages fall back to CPU transparently.

---

## 🗺️ Roadmap

| Stage | Status | Description |
|---|---|---|
| [MVP] Vectorized Normalization | ✅ Complete | 14-day rolling Z-score, CUDA-accelerated |
| [MVP] Synthetic Alpha Generator | ✅ Complete | 1M-tick signal, chunked GPU processing, Astra persistence |
| [V2] Integrated Vector Pipelines | Planned | Astra `$vectorize` for unstructured macroeconomic metadata ingestion |
| [V3] Distributed Feature Factory | Planned | Ray clusters for multi-node GPU training and cross-asset signal backtesting |
