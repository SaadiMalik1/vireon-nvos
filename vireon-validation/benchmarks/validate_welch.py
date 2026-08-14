import numpy as np
import scipy.signal
from vireon_core.contracts.base import ISignal
from vireon_methods.base import WelchPSD

def benchmark_welch():
    print("=== VIREON Scientific Benchmark: Welch PSD ===")
    
    # 1. Generate Synthetic Ground Truth
    fs = 250.0
    t = np.arange(0, 10, 1/fs)
    from vireon_core.runtime.rng import DeterministicRNG
    rng = DeterministicRNG(seed=42)
    # 10Hz alpha + 50Hz line noise + white noise
    data = np.sin(2 * np.pi * 10 * t) + 0.5 * np.sin(2 * np.pi * 50 * t) + rng.normal(0.0, 1.0, len(t))
    
    signal = ISignal(sampling_rate=fs, data=data)
    
    # 2. Run VIREON Method
    plugin = WelchPSD(nperseg=256)
    vireon_output = plugin.execute({"signal": signal})["psd"].data
    
    # 3. Run Reference Implementation (SciPy)
    f, reference_output = scipy.signal.welch(data, fs=fs, nperseg=256, axis=0)
    
    # 4. Compute Agreement Statistics
    rmse = np.sqrt(np.mean((vireon_output - reference_output)**2))
    mae = np.mean(np.abs(vireon_output - reference_output))
    pearson_r = np.corrcoef(vireon_output, reference_output)[0, 1]
    
    print(f"RMSE: {rmse:.10e}")
    print(f"MAE: {mae:.10e}")
    print(f"Pearson r: {pearson_r:.5f}")
    
    if rmse < 1e-10:
        print("RESULT: PASS (Numerical Agreement Confirmed)")
    else:
        print("RESULT: FAIL")

if __name__ == "__main__":
    benchmark_welch()
