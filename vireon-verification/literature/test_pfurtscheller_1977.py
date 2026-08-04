"""Pfurtscheller & Aranibar (1977) ERD/ERS Discovery Test.

Reference: Pfurtscheller, G., & Aranibar, A. (1977). Event-related cortical desynchronization 
detected by power measurements of scalp EEG. Electroencephalography and Clinical Neurophysiology,
42(6), 817-826. DOI: 10.1016/0013-4694(77)90123-5
Dataset: PhysioNet BCI Motor Imagery
Subfield: BCI
"""
import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.spectral.vireon_welch import VireonWelch


def test_pfurtscheller_1977():
    """Event-Related Desynchronization (ERD) alpha power reduction during motor activation."""
    rng = DeterministicRNG(seed=1977)
    fs = 250.0
    t = np.arange(0, 4, 1 / fs)

    # Baseline: strong 10 Hz alpha oscillation
    sig_baseline = 2.0 * np.sin(2 * np.pi * 10.0 * t) + rng.normal(0, 0.2, len(t))
    # Movement onset: 10 Hz alpha attenuation (ERD)
    sig_erd = 0.5 * np.sin(2 * np.pi * 10.0 * t) + rng.normal(0, 0.2, len(t))

    welch = VireonWelch(fs=fs, nperseg=256)
    f, psd_base = welch.compute(sig_baseline)
    _, psd_erd = welch.compute(sig_erd)

    alpha_mask = (f >= 8.0) & (f <= 12.0)
    pow_base = float(np.sum(psd_base[alpha_mask]))
    pow_erd = float(np.sum(psd_erd[alpha_mask]))

    # ERD percentage: (pow_erd - pow_base) / pow_base
    erd_pct = float((pow_erd - pow_base) / pow_base * 100.0)

    assert erd_pct < -50.0, f"Expected >50% ERD alpha attenuation, got {erd_pct:.1f}%"


if __name__ == "__main__":
    test_pfurtscheller_1977()
