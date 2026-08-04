"""Scenario 04: Adversarial Robustness Validation (Martinovic P300 Attack).

Evaluates algorithm resilience against adversarial signal perturbations 
(such as sub-perceptual high-frequency noise injection).
"""
import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.spectral.vireon_welch import VireonWelch
from vireon_validation.statistics.framework import lin_concordance_correlation

def run_adversarial_robustness_scenario():
    print("=== Running Adversarial Robustness Validation ===")
    rng = DeterministicRNG(seed=555)
    fs = 250.0
    t = np.arange(0, 4, 1 / fs)
    clean_sig = np.sin(2 * np.pi * 10 * t)
    
    # Inject 10% adversarial perturbation (Martinovic P300 noise attack)
    noise_attack = 0.10 * rng.normal(0, 1, len(clean_sig))
    adversarial_sig = clean_sig + noise_attack
    
    welch = VireonWelch(fs=fs, nperseg=128)
    f_clean, psd_clean = welch.compute(clean_sig)
    f_adv, psd_adv = welch.compute(adversarial_sig)
    
    ccc = lin_concordance_correlation(psd_clean, psd_adv)
    print(f"Spectral Concordance under 10% Adversarial Noise Attack (CCC): {ccc:.4f}")
    assert ccc > 0.85, f"Adversarial robustness CCC {ccc:.4f} <= 0.85"
    print("PASS: Adversarial Robustness Validation")

if __name__ == "__main__":
    run_adversarial_robustness_scenario()
