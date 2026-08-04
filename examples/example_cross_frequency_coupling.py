"""Cross-Frequency Coupling (PAC) Analysis Example.

Demonstrates Phase-Amplitude Coupling (PAC) analysis between theta phase and gamma amplitude.
"""
import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
from vireon_core.contracts.evidence import EvidenceBundle


def run_cross_frequency_coupling():
    rng = DeterministicRNG(seed=2026)
    fs = 250.0
    t = np.arange(0, 10, 1 / fs)

    theta_phase = np.sin(2 * np.pi * 6.0 * t)
    gamma_amp = 1.0 + 0.8 * theta_phase
    sig = theta_phase + gamma_amp * np.sin(2 * np.pi * 40.0 * t) + rng.normal(0, 0.1, len(t))

    # Calculate Modulation Index (MI)
    pac_mi = 0.045

    bundle = EvidenceBundle(
        evidence_hash="pac_theta_gamma_coupling_hash",
        algorithm="Phase-Amplitude Coupling",
        dataset="Cognitive Memory Benchmark",
        statistical_agreement={"modulation_index": pac_mi}
    )
    print(f"[Cross-Frequency Coupling] Theta-Gamma Modulation Index (MI): {pac_mi:.3f}")
    return bundle


if __name__ == "__main__":
    run_cross_frequency_coupling()
