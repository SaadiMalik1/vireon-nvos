import numpy as np
import os
from scipy.signal import welch

def generate_psd_reference():
    fs = 250.0
    t = np.arange(0, 10.0, 1.0/fs)
    # create a deterministic signal: 10Hz sine wave + 50Hz sine wave + some noise
    np.random.seed(42)
    signal = 2.0 * np.sin(2 * np.pi * 10.0 * t) + 0.5 * np.sin(2 * np.pi * 50.0 * t) + 0.1 * np.random.randn(len(t))
    
    freqs, psd = welch(signal, fs=fs, nperseg=256)
    
    os.makedirs(os.path.join(os.environ.get("VIREON_HOME", "."), "vireon-reference/reference"), exist_ok=True)
    np.save(os.path.join(os.environ.get("VIREON_HOME", "."), "vireon-reference/reference/test_signal.npy"), signal)
    np.save(os.path.join(os.environ.get("VIREON_HOME", "."), "vireon-reference/reference/scipy_psd.npy"), psd)
    np.save(os.path.join(os.environ.get("VIREON_HOME", "."), "vireon-reference/reference/scipy_psd_freqs.npy"), freqs)
    print("Generated PSD references.")

if __name__ == "__main__":
    generate_psd_reference()
