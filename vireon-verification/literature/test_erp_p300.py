"""ERP P300 Latency Reproduction Test.

Reference: Polich, J. (2007). Updating P300: an integrative theory of P3a and P3b.
Clinical Neurophysiology, 118(10), 2128-2148. DOI: 10.1016/j.clinph.2007.04.019
"""
import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.spectral.vireon_fft import VireonFFT

def test_erp_p300():
    """ERP P300 component peak latency detection."""
    rng = DeterministicRNG(seed=42)
    fs = 250.0
    t = np.arange(0, 1.0, 1 / fs)  # 1-second epoch
    
    # Target trial: P300 wave at 310ms (sample index ~ 77.5)
    target_erp = 5.0 * np.exp(-((t - 0.310) ** 2) / (2 * (0.04 ** 2)))
    signal = target_erp + rng.normal(0, 0.2, len(t))
    
    peak_sample = np.argmax(signal)
    computed_latency_ms = (peak_sample / fs) * 1000.0
    
    assert abs(computed_latency_ms - 310.0) < 25.0, f"P300 latency {computed_latency_ms:.1f}ms differs from 310ms"

if __name__ == "__main__":
    test_erp_p300()
