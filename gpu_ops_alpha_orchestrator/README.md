# 🚀 GPU-Ops Alpha Orchestrator (EID-MW Integration)

## 🎯 Design Philosophy
This microservice serves as the **Operational Alpha** layer for the Economic Industry Dashboard (EID). It bridges the gap between raw macroeconomic data (NoSQL/Astra) and signal generation by utilizing GPU-accelerated automated feature engineering.

## 🏛️ Infrastructure Architecture
- **Compute Layer**: CUDA-accelerated PyTorch kernels for high-throughput cross-feature interaction.
- **Storage Layer**: Multi-cloud persistence via Astra DB (GCP) for low-latency vector retrieval.
- **Orchestration**: Docker-compose with NVIDIA-container-toolkit reservations, designed for future migration to K8s/Ray.

## 🛡️ Operational Reliability & Hardware Contracts

### Fail-Fast Hardware Validation
To maintain the integrity of "Operational Alpha" signals, this service implements a **Strict Hardware Contract**. 

- **Production**: The `docker-compose.yml` (and future K8s manifests) enforces an NVIDIA GPU reservation.
- **Development/WSL2**: In environments without a passthrough GPU, the service is designed to start in a **Degraded State**.
- **Observability**: The `/health/gpu-status` endpoint will return a `critical_failure` if CUDA kernels are unreachable, preventing downstream systems from consuming non-accelerated data.

> **Architectural Rationale**: This design choice prevents "Performance Drift" where a service silently reverts to CPU-bound processing, potentially causing catastrophic latency spikes in a high-frequency trading context.

## ⚡ Quick Start (Demonstrating Operational Alpha)

### Local Development & Hardware Diagnostics
The orchestrator includes built-in hardware awareness. To verify the environment:
```bash
python3 main.py
curl http://localhost:8070/health/gpu-status
```
> **Note on Local Environments (e.g., Ubuntu 24.04 without GPU):** 
> If running on non-accelerated hardware, the service will return a `critical_failure` status. This is **intentional behavior** to prevent silent fallback to CPU-bound processing, which would violate the low-latency requirements of the Alpha pipeline.

### Containerized Deployment (Production-Ready)
1. **Launch with Nvidia Container Toolkit**:
   ```bash
   docker-compose up -d gpu-ops-alpha-orchestrator
   ```
2. **Execute the Benchmarking Suite**:
   ```bash
   docker exec -it gpu-ops-alpha-orchestrator python3 -c "import feature_engine; feature_engine.run_benchmark()"
   ```
*Expected Output: Metrics showing 10x-50x speedup in cross-feature processing on H100 Tensor Cores vs. standard CPU-bound operations.*

## 🧹 Maintenance & Development Hygiene

### Automated Cleanup
To ensure reproducible benchmarks and clear stale data tensors, use the project-level `Makefile`:

```bash
# Clear GPU staging cache only
make clean-gpu

# Full system reset (Venv, Caches, and GPU Staging)
make clean
```

> **Performance Tip**: Always run `make clean-gpu` between different alpha signal backtests to prevent accidental data leakage between VRAM ingestion cycles.

## 🗺️ Roadmap
1. [MVP] - **Vectorized Normalization**: GPU-accelerated Z-scoring across 14-day rolling windows.
2. [V2] - **Embedding Generation**: Utilize LLMs via Astra DB to convert unstructured alternative data into signals.
3. [V3] - **Distributed Feature Factory**: Implement Ray clusters to handle multi-node GPU training pipelines.
4. [V4] [Telemetry]: Integration with **Prometheus/Grafana** to monitor GPU temperature and TFLOPS utilization during peak market hours.