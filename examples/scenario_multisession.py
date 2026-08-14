import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.spectral.vireon_welch import VireonWelch
from vireon_validation.statistics.icc import intraclass_correlation

def run_multisession_scenario():
    print("=== Running Multi-Session Test-Retest Reliability Validation ===")
    fs = 250.0
    t = np.arange(0, 10, 1 / fs)
    welch = VireonWelch(fs=fs, nperseg=256)
    
    n_subjects = 5
    sub_freqs = [8.0, 9.5, 10.5, 11.5, 12.5]
    psd_session1 = []
    psd_session2 = []
    
    for sub_idx, f_alpha in enumerate(sub_freqs):
        base_sig = np.sin(2 * np.pi * f_alpha * t)
        
        # Session 1
        rng1 = DeterministicRNG(seed=100 + sub_idx)
        sig1 = base_sig + rng1.normal(0, 0.1, len(t))
        f1, p1 = welch.compute(sig1)
        
        # Session 2
        rng2 = DeterministicRNG(seed=200 + sub_idx)
        sig2 = base_sig + rng2.normal(0, 0.1, len(t))
        f2, p2 = welch.compute(sig2)
        
        alpha_mask = (f1 >= 8.0) & (f1 <= 13.0)
        psd_session1.append(float(np.max(p1[alpha_mask])))
        psd_session2.append(float(np.max(p2[alpha_mask])))
        
    data = np.column_stack([psd_session1, psd_session2])
    icc_score = intraclass_correlation(data)
    print(f"Test-Retest Intraclass Correlation Coefficient (ICC): {icc_score:.4f} across {n_subjects} subjects")
    assert icc_score > 0.85, f"Test-retest ICC {icc_score:.4f} <= 0.85"
    print("PASS: Multi-Session Test-Retest Validation")

if __name__ == "__main__":
    run_multisession_scenario()
