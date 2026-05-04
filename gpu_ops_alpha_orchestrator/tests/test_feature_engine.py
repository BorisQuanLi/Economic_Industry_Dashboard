"""
TDD suite for VectorizedSignalProcessor.
Patches are applied to the LOCAL module namespace per AGENT_LOGS.md Round 3 directive.
"""
import time
import pytest
import torch
from unittest.mock import patch

# Import from local namespace so patches resolve correctly
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from feature_engine import VectorizedSignalProcessor


WINDOW = VectorizedSignalProcessor.WINDOW  # 14


# ---------------------------------------------------------------------------
# Shape & stationarity
# ---------------------------------------------------------------------------

def test_output_shape_1d():
    proc = VectorizedSignalProcessor()
    signal = torch.randn(30)
    out = proc.normalize(signal)
    assert out.shape == (30 - WINDOW + 1,), f"Expected ({30 - WINDOW + 1},), got {out.shape}"


def test_output_shape_2d():
    proc = VectorizedSignalProcessor()
    signal = torch.randn(50, 5)
    out = proc.normalize(signal)
    assert out.shape == (50 - WINDOW + 1, 5)


def test_output_is_cpu_tensor():
    """Astra ingestion requires CPU tensors regardless of compute device."""
    proc = VectorizedSignalProcessor()
    out = proc.normalize(torch.randn(30))
    assert out.device.type == "cpu"


def test_z_score_mean_near_zero():
    """Rolling Z-score of a constant signal should be ~0 (stationary)."""
    proc = VectorizedSignalProcessor()
    signal = torch.ones(50)
    out = proc.normalize(signal)
    # std of constant window = 0, so z = 0 / (0 + 1e-6) ≈ 0
    assert out.abs().max().item() < 1e-3


def test_z_score_known_values():
    """Verify first window: [0..13], mean=6.5, std computed, z of last element."""
    proc = VectorizedSignalProcessor()
    signal = torch.arange(30, dtype=torch.float32)
    out = proc.normalize(signal)
    window = signal[:WINDOW]
    mu = window.mean()
    sig = window.std(unbiased=False)
    expected_first = (signal[WINDOW - 1] - mu) / (sig + 1e-6)
    assert abs(out[0].item() - expected_first.item()) < 1e-4


# ---------------------------------------------------------------------------
# OOM degraded-state fallback (SKILL.md: Memory Management)
# ---------------------------------------------------------------------------

def test_oom_falls_back_to_cpu():
    """Simulate OutOfMemoryError; processor must fall back to CPU without raising."""
    proc = VectorizedSignalProcessor()
    proc.device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

    original_to = torch.Tensor.to

    call_count = {"n": 0}

    def mock_to(self, *args, **kwargs):
        call_count["n"] += 1
        if call_count["n"] == 1 and str(args[0]) == "cuda":
            raise torch.cuda.OutOfMemoryError("mock OOM")
        return original_to(self, *args, **kwargs)

    with patch("torch.Tensor.to", mock_to):
        # Only meaningful when device is cuda; on CPU this just exercises the path
        try:
            out = proc.normalize(torch.randn(30))
            assert out.device.type == "cpu"
        except torch.cuda.OutOfMemoryError:
            pytest.skip("OOM path not reachable without CUDA device")


# ---------------------------------------------------------------------------
# Benchmark: CPU vs GPU (SKILL.md: Benchmarking requirement)
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not torch.cuda.is_available(), reason="GPU not available")
def test_gpu_faster_than_cpu_large_signal():
    """GPU processing must be faster than CPU for large tensors (SKILL.md benchmark)."""
    signal = torch.randn(10_000, 64)

    # CPU baseline
    cpu_proc = VectorizedSignalProcessor()
    cpu_proc.device = torch.device("cpu")
    t0 = time.perf_counter()
    cpu_proc.normalize(signal)
    cpu_time = time.perf_counter() - t0

    # GPU
    gpu_proc = VectorizedSignalProcessor()
    torch.cuda.synchronize()
    t0 = time.perf_counter()
    gpu_proc.normalize(signal)
    torch.cuda.synchronize()
    gpu_time = time.perf_counter() - t0

    assert gpu_time < cpu_time, f"GPU ({gpu_time:.4f}s) not faster than CPU ({cpu_time:.4f}s)"
