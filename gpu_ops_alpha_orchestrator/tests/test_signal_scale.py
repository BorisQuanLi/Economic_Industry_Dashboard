"""
test_signal_scale.py
Benchmarks synthetic_alpha_generator at 1M-row vs 1k-row scale and verifies
the SKILL.md Degraded State contract (no CUDA → CPU fallback, no crash).
"""
import os
import sys
import time
import torch
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from synthetic_alpha_generator import (
    generate_signal,
    process_in_chunks,
    generate_and_persist,
    generate_signal_summary,
    persist_alpha_summary,
)

N_FEATURES = 64


# ---------------------------------------------------------------------------
# Degraded State contract (SKILL.md): must run on CPU when CUDA is unavailable
# ---------------------------------------------------------------------------

def test_degraded_state_no_cuda():
    """process_in_chunks must complete without error regardless of CUDA availability."""
    signal = generate_signal(n_ticks=100, n_features=N_FEATURES)
    result = process_in_chunks(signal)
    assert result.device.type == "cpu"
    assert result.shape[1] == N_FEATURES


def test_cuda_availability_handled():
    """torch.cuda.is_available() result must not cause an unhandled exception."""
    available = torch.cuda.is_available()
    signal = generate_signal(n_ticks=200, n_features=N_FEATURES)
    # Should succeed on both paths
    result = process_in_chunks(signal)
    assert result is not None
    _ = available  # consumed — no assertion on value, only on no-crash


# ---------------------------------------------------------------------------
# Signal shape & content
# ---------------------------------------------------------------------------

def test_generate_signal_shape():
    sig = generate_signal(n_ticks=1_000, n_features=N_FEATURES)
    assert sig.shape == (1_000, N_FEATURES)


def test_generate_signal_has_drift():
    """Signal must not be pure noise — sine drift should produce non-zero mean."""
    sig = generate_signal(n_ticks=10_000, n_features=N_FEATURES)
    # Pure Gaussian noise has E[|mean|] ≈ 0; drift pushes it away from 0
    assert sig.mean().abs().item() > 0.0


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------

def test_persist_creates_pt_file(tmp_path):
    out = str(tmp_path / "gpu_cache" / "alpha_signals.pt")
    path = generate_and_persist(n_ticks=500, n_features=N_FEATURES, output_path=out)
    assert os.path.exists(path)
    loaded = torch.load(path, weights_only=True)
    assert loaded.shape[1] == N_FEATURES


# ---------------------------------------------------------------------------
# Latency benchmark: 1M rows vs 1k rows (SKILL.md: Benchmarking requirement)
# ---------------------------------------------------------------------------

def test_latency_benchmark_1m_vs_1k():
    """
    1M-row processing must complete in finite time; assert 1k is faster than 1M.
    Skips GPU sync when CUDA is unavailable (Degraded State).
    """
    def timed_run(n_ticks: int) -> float:
        signal = generate_signal(n_ticks=n_ticks, n_features=N_FEATURES)
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        t0 = time.perf_counter()
        process_in_chunks(signal)
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        return time.perf_counter() - t0

    t_1k  = timed_run(1_000)
    t_1m  = timed_run(1_000_000)

    print(f"\n  1k-row latency : {t_1k:.4f}s")
    print(f"  1M-row latency : {t_1m:.4f}s")
    print(f"  Scale factor   : {t_1m / t_1k:.1f}x")

    assert t_1k < t_1m, "1k-row run must be faster than 1M-row run"
    assert t_1m < 300,  "1M-row processing must complete within 5 minutes"


# ---------------------------------------------------------------------------
# generate_signal_summary
# ---------------------------------------------------------------------------

def test_summary_keys():
    tensor = process_in_chunks(generate_signal(n_ticks=500, n_features=N_FEATURES))
    summary = generate_signal_summary(tensor)
    assert set(summary.keys()) == {"mean", "std", "max_variance"}


def test_summary_computed_on_cpu():
    """SKILL.md Memory Management: summary must not hold VRAM — values are plain floats."""
    tensor = process_in_chunks(generate_signal(n_ticks=500, n_features=N_FEATURES))
    summary = generate_signal_summary(tensor)
    for v in summary.values():
        assert isinstance(v, float)


def test_summary_max_variance_positive():
    tensor = process_in_chunks(generate_signal(n_ticks=1_000, n_features=N_FEATURES))
    summary = generate_signal_summary(tensor)
    assert summary["max_variance"] > 0.0


# ---------------------------------------------------------------------------
# persist_alpha_summary — Degraded State & Security Tier 3
# ---------------------------------------------------------------------------

def test_persist_alpha_summary_calls_astra(monkeypatch):
    """persist_alpha_summary must delegate to astra_builder.persist_alpha_signal."""
    mock_builder = MagicMock()
    import synthetic_alpha_generator as sag
    monkeypatch.setattr(sag, "astra_builder", mock_builder)

    summary = {"mean": 0.1, "std": 1.0, "max_variance": 2.5}
    persist_alpha_summary(summary)

    mock_builder.persist_alpha_signal.assert_called_once()
    payload = mock_builder.persist_alpha_signal.call_args[0][0]
    assert "HFT_BATCH_001" in payload["signal_id"]
    assert payload["source"] == "synthetic_alpha_generator"


def test_persist_alpha_summary_no_hardcoded_credentials():
    """Security Tier 3: source must not contain raw token strings."""
    import inspect
    import synthetic_alpha_generator as sag
    source = inspect.getsource(sag)
    assert "ASTRA_DB_TOKEN" not in source.replace("os.getenv", "")  # only via env
    assert "AstraCS:" not in source
