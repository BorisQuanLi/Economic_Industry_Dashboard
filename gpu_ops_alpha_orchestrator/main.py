import os
import torch
import uvicorn
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from feature_engine import generate_alpha_features, run_benchmark

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- INFRASTRUCTURE SIGNAL: Pre-warm H100/CUDA Kernels ---
    # Prevents first-request latency spikes in production
    if torch.cuda.is_available():
        print("Initializing H100 Tensor Cores & warming CUDA kernels...")
        dummy_tensor = torch.randn(1, 10).to("cuda")
        del dummy_tensor
    yield

app = FastAPI(
    title="GPU-Ops Alpha Orchestrator",
    version="1.1.0",
    lifespan=lifespan
)

@app.get("/")
@app.get("/health/gpu-status")
async def gpu_health_check():
    """Enterprise health check for GPU compute nodes."""
    gpu_ready = torch.cuda.is_available()
    status_code = "online" if gpu_ready else "degraded"
    
    details = {
        "status": status_code,
        "cuda_version": torch.version.cuda,
        "device_count": torch.cuda.device_count(),
        "current_device": torch.cuda.get_device_name(0) if gpu_ready else "none",
        "astra_integration": "active" if os.getenv("ASTRA_DB_APPLICATION_TOKEN") else "missing_token",
        "embedding_provider": os.getenv("EMBEDDING_MODEL_ID", "nvidia/nv-embedqa-e5-v5")
    }
    
    if not gpu_ready:
        # Business Logic: Compute nodes without GPUs are mission-critical failures
        return {"status": "critical_failure", "reason": "No CUDA devices found on H100-labeled node"}
        
    return details

@app.post("/process-signals")
async def process_signals(payload: list[list[float]]):
    """Entry point for automated feature engineering."""
    if not torch.cuda.is_available():
        raise HTTPException(status_code=503, detail="GPU Acceleration Unavailable")
    
    data_tensor = torch.tensor(payload).to("cuda")
    features = generate_alpha_features(data_tensor)
    return {"processed_features": features.tolist()}

if __name__ == "__main__":
    # Local dev entry point
    uvicorn.run(app, host="0.0.0.0", port=8070)
