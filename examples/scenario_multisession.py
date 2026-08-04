"""Scenario 02: Multi-Session Test-Retest Reliability Validation.

Evaluates test-retest reliability across multiple simulated sessions 
and quantifies intra-class correlation (ICC) / Concordance Correlation Coefficient (CCC).
"""
import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.spectral.vireon_welch import VireonWelch
from vireon_validation.statistics.framework import lin_concordance_correlation

def run_multisession_scenario():
    print("=== Running Multi-Session Test-Retest Reliability Validation ===")
    fs = 250.0
    t = np.arange(0, 10, 1 / fs)
    base_signal = np.sin(2 * np.pi * 10 * t) + 0.5 * np.sin(2 * np.pi * 20 * t)
    
    # Session 1 (Session A recording)
    rng1 = DeterministicRNG(seed=101)
    sig1 = base_signal + rng1.normal(0, 0.2, len(t))
    welch = VireonWelch(fs=fs, nperseg=256)
    f1, psd1 = welch.compute(sig1)
    
    # Session 2 (Session B retest recording with noise)
    rng2 = DeterministicRNG(seed=202)
    sig2 = base_signal + rng2.normal(0, 0.2, len(t))
    f2, psd2 = welch.compute(sig2)
    
    ccc = lin_concordance_correlation(psd1, psd2)
    print(f"Test-Retest Spectral Concordance (CCC): {ccc:.4f}")
    assert ccc > 0.90, f"Test-retest CCC {ccc:.4f} <= 0.90"
    print("PASS: Multi-Session Test-Retest Validation")

if __name__ == "__main__":
    run_multisession_scenario()
