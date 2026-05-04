"""
synthetic_alpha_generator.py
Generates a [1_000_000, 64] market-signal tensor (Gaussian noise + sine drift)
and feeds it into generate_alpha_features() in chunks to stay under the 8 GB
VRAM threshold defined in SKILL.md.

Astra integration: generate_signal_summary() + persist_alpha_summary() wire the
batch statistical fingerprint into the alpha_signals Astra collection.
"""
import os
import math
import sys
import datetime
import torch

# Cross-context import (explicit permission granted in SOW)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from etl_service.src.adapters.astra_vector_builder import astra_builder
from feature_engine import generate_alpha_features

# SKILL.md: VRAM Threshold — 8 GB hard stop in dev-sandbox
# float32 bytes per element: 4
# Chunk size chosen so one chunk ≈ 64 * CHUNK_ROWS * 4 bytes stays well under 8 GB.
CHUNK_ROWS: int = 50_000          # 50k × 64 × 4 B ≈ 12.8 MB per chunk
CACHE_DIR: str = "gpu_cache"
OUTPUT_PATH: str = os.path.join(CACHE_DIR, "alpha_signals.pt")


def generate_signal(n_ticks: int = 1_000_000, n_features: int = 64) -> torch.Tensor:
    """
    Build a [n_ticks, n_features] tensor:
      - Gaussian noise  (σ=1, μ=0)
      - + sine-wave drift on each feature (simulates price momentum)
    """
    t = torch.linspace(0, 4 * math.pi, n_ticks)          # (T,)
    # Each feature gets a slightly different frequency to break symmetry
    freqs = torch.linspace(1.0, 2.0, n_features)          # (F,)
    drift = torch.sin(t.unsqueeze(1) * freqs.unsqueeze(0))  # (T, F)
    noise = torch.randn(n_ticks, n_features)
    return noise + drift                                   # (T, F)


def process_in_chunks(signal: torch.Tensor, chunk_rows: int = CHUNK_ROWS) -> torch.Tensor:
    """
    Feed signal into generate_alpha_features() in chunks.
    SKILL.md Memory Management: catches OutOfMemoryError, empties cache, retries on CPU.
    Returns the full processed tensor on CPU.
    """
    results = []
    for start in range(0, signal.shape[0], chunk_rows):
        chunk = signal[start: start + chunk_rows]
        try:
            results.append(generate_alpha_features(chunk))
        except torch.cuda.OutOfMemoryError:
            torch.cuda.empty_cache()
            # CPU fallback for this chunk
            device_backup = torch.device("cpu")
            results.append(generate_alpha_features(chunk.to(device_backup)))
    return torch.cat(results, dim=0)


def generate_and_persist(
    n_ticks: int = 1_000_000,
    n_features: int = 64,
    output_path: str = OUTPUT_PATH,
) -> str:
    """
    Full pipeline: generate → process → serialize to gpu_cache/ as .pt file.
    Returns the output path for zero-copy handoff.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    signal = generate_signal(n_ticks, n_features)
    processed = process_in_chunks(signal)
    torch.save(processed, output_path)
    return output_path


def generate_signal_summary(tensor: torch.Tensor) -> dict:
    """
    Statistical fingerprint of the processed batch.
    SKILL.md Memory Management: computed on CPU after GPU work is cat-ed,
    so no VRAM is held during I/O.
    """
    cpu = tensor.cpu()                          # ensure CPU — no VRAM held
    per_feature_var = cpu.var(dim=0)            # (F,)
    return {
        "mean":         cpu.mean().item(),
        "std":          cpu.std().item(),
        "max_variance": per_feature_var.max().item(),
    }


def persist_alpha_summary(summary: dict) -> None:
    """
    Push the batch statistical fingerprint to the alpha_signals Astra collection.
    _id = ISO timestamp + 'HFT_BATCH_001' for traceability.
    Security Tier 3: no credentials hardcoded; astra_builder sources from env.
    """
    batch_id = f"{datetime.datetime.utcnow().isoformat()}_HFT_BATCH_001"
    astra_builder.persist_alpha_signal({
        "signal_id": batch_id,
        "content":   str(summary),   # $vectorize field — embedded by H100 provider
        "source":    "synthetic_alpha_generator",
    })


if __name__ == "__main__":
    # Full pipeline: Generate 1M → Compute GPU Features → Summarize → Persist to Astra
    signal    = generate_signal()
    processed = process_in_chunks(signal)

    os.makedirs(CACHE_DIR, exist_ok=True)
    torch.save(processed, OUTPUT_PATH)
    print(f"Alpha signals written to {OUTPUT_PATH}  shape={processed.shape}")

    summary = generate_signal_summary(processed)
    print(f"Statistical fingerprint: {summary}")

    persist_alpha_summary(summary)
    print("Summary persisted to Astra alpha_signals collection.")
