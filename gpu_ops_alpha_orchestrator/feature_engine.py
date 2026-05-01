import time
import torch

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
