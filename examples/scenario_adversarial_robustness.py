import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.spectral.vireon_welch import VireonWelch
from vireon_validation.statistics.framework import lin_concordance_correlation

def run_adversarial_robustness_scenario():
    print("=== Running Adversarial Robustness Validation ===")
    fs = 250.0
    t = np.arange(0, 4, 1 / fs)
    clean_sig = np.sin(2 * np.pi * 10 * t)
    
    # Crafted Fast Gradient Sign Method (FGSM) adversarial perturbation attack
    # Target: Phase-cancelling gradient perturbation to test spectral robustness
    epsilon = 0.08
    grad_target = -np.sin(2 * np.pi * 10 * t)
    crafted_fgsm_perturbation = epsilon * np.sign(grad_target)
    
    adversarial_sig = clean_sig + crafted_fgsm_perturbation
    
    welch = VireonWelch(fs=fs, nperseg=128)
    f_clean, psd_clean = welch.compute(clean_sig)
    f_adv, psd_adv = welch.compute(adversarial_sig)
    
    ccc = lin_concordance_correlation(psd_clean, psd_adv)
    print(f"Spectral Concordance under Crafted FGSM Adversarial Perturbation Attack (CCC): {ccc:.4f}")
    assert ccc > 0.70, f"Adversarial robustness CCC {ccc:.4f} <= 0.70"
    print("PASS: Adversarial Robustness Validation")

if __name__ == "__main__":
    run_adversarial_robustness_scenario()
