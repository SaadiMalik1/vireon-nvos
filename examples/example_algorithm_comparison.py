"""Algorithm Comparison Example: Welch vs Multitaper PSD Estimation.

Demonstrates statistical cross-validation between spectral estimation methods.
"""
import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.spectral.vireon_welch import VireonWelch
from vireon_methods.spectral.vireon_multitaper import VireonMultitaper
from vireon_validation.statistics.framework import lin_concordance_correlation
from vireon_core.contracts.evidence import EvidenceBundle


def run_algorithm_comparison():
    rng = DeterministicRNG(seed=2026)
    fs = 250.0
    t = np.arange(0, 4, 1 / fs)
    sig = np.sin(2 * np.pi * 10.0 * t) + rng.normal(0, 0.5, len(t))

    welch = VireonWelch(fs=fs, nperseg=256)
    f_w, psd_w = welch.compute(sig)

    mt = VireonMultitaper(fs=fs, NW=2.5)
    f_m, psd_m = mt.compute(sig)

    # Interp multitaper onto Welch frequency grid
    psd_m_interp = np.interp(f_w, f_m, psd_m)
    ccc = float(lin_concordance_correlation(psd_w, psd_m_interp))

    bundle = EvidenceBundle(
        evidence_hash="algorithm_comparison_welch_multitaper_hash",
        algorithm="Welch vs Multitaper Comparison",
        dataset="Synthetic EEG Benchmark",
        statistical_agreement={"ccc": ccc}
    )
    print(f"[Algorithm Comparison] Welch vs Multitaper CCC: {ccc:.4f}")
    return bundle


if __name__ == "__main__":
    run_algorithm_comparison()
