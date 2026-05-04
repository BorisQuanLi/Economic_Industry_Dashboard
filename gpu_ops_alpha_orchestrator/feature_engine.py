import time
import torch
from torch import Tensor


class VectorizedSignalProcessor:
    """14-day rolling Z-score normalization via CUDA-accelerated PyTorch unfold."""

    WINDOW = 14

    def __init__(self) -> None:
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    @torch.no_grad()
    def normalize(self, signal: Tensor) -> Tensor:
        """
        Args:
            signal: 1-D or 2-D tensor of shape (T,) or (T, F).
        Returns:
            Stationary Z-score tensor of same shape, on CPU, ready for Astra ingestion.
        """
        squeeze = signal.dim() == 1
        if squeeze:
            signal = signal.unsqueeze(1)          # (T, 1)

        try:
            x = signal.to(self.device)            # (T, F)
        except torch.cuda.OutOfMemoryError:
            torch.cuda.empty_cache()
            x = signal.to("cpu")

        T, F = x.shape
        # unfold: (T - W + 1, F, W)  — fully vectorized, zero Python loops
        windows = x.unfold(0, self.WINDOW, 1)     # (T-W+1, F, W)
        mu  = windows.mean(dim=-1)                # (T-W+1, F)
        sig = windows.std(dim=-1, unbiased=False) # (T-W+1, F)
        z   = (x[self.WINDOW - 1:] - mu) / (sig + 1e-6)  # (T-W+1, F)

        if squeeze:
            z = z.squeeze(1)
        return z.cpu()


@torch.no_grad() # Prevents tracking history (and using memory) for computations
def generate_alpha_features(market_data_tensor):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    data = market_data_tensor.to(device)
    
    # Efficient tensor ops
    mean = data.mean(dim=0)
    std = data.std(dim=0)
    features = (data - mean) / (std + 1e-6)
    
    return features.cpu() # Return as tensor for better downstream flexibility

def run_benchmark():
    # Mock data: 1 million rows, 10 features
    data = torch.randn(1000000, 10)
    
    # CPU Time
    start = time.time()
    cpu_res = (data - data.mean(0)) / data.std(0)
    cpu_time = time.time() - start
    
    # GPU Time
    start = time.time()
    gpu_res = generate_alpha_features(data)
    gpu_time = time.time() - start
    
    print(f"🚀 Operational Alpha Benchmarked:")
    print(f"   CPU Processing: {cpu_time:.4f}s")
    print(f"   GPU Processing: {gpu_time:.4f}s")
    print(f"   Speedup: {cpu_time/gpu_time:.1f}x")

    return {
        "cpu_seconds": round(cpu_time, 4),
        "gpu_seconds": round(gpu_time, 4),
        "speedup": f"{round(cpu_time/gpu_time, 1)}x"
    }
