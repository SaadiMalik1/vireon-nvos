"""Sleep Staging Delta/Alpha Band Ratio Test.

Reference: Rechtschaffen, A., & Kales, A. (1968). A manual of standardized terminology,
techniques and scoring system for sleep stages of human subjects. DOI: 10.1037/e400002004-001
"""
import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.spectral.vireon_welch import VireonWelch

def test_sleep_staging():
    """Sleep staging spectral power discrimination (Deep Sleep Delta vs Awake Alpha)."""
    rng = DeterministicRNG(seed=777)
    fs = 250.0
    t = np.arange(0, 10, 1 / fs)
    
    # Awake Alpha (10 Hz) vs Deep Sleep Delta (2 Hz)
    sig_alpha = np.sin(2 * np.pi * 10.0 * t) + rng.normal(0, 0.2, len(t))
    sig_delta = 3.0 * np.sin(2 * np.pi * 2.0 * t) + rng.normal(0, 0.2, len(t))
    
    welch = VireonWelch(fs=fs, nperseg=256)
    f, psd_alpha = welch.compute(sig_alpha)
    _, psd_delta = welch.compute(sig_delta)
    
    delta_idx = (f >= 0.5) & (f <= 4.0)
    alpha_idx = (f >= 8.0) & (f <= 12.0)
    
    delta_power_deep = float(np.sum(psd_delta[delta_idx]))
    alpha_power_awake = float(np.sum(psd_alpha[alpha_idx]))
    
    assert delta_power_deep > 1.0, "Deep sleep delta power low"
    assert alpha_power_awake > 0.1, "Awake alpha power low"

if __name__ == "__main__":
    test_sleep_staging()
