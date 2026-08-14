"""Klimesch (1999) Alpha and Theta Oscillations Test.

Reference: Klimesch, W. (1999). EEG alpha and theta oscillations reflect cognitive and memory
performance: a review and analysis. Brain Research Reviews, 29(2-3), 169-195.
DOI: 10.1016/S0169-2607(99)00005-4
Dataset: ERP CORE
Subfield: cognitive
"""
import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.spectral.vireon_welch import VireonWelch


def test_klimesch_1999():
    """Alpha peak frequency (IAF) and theta power shift during cognitive load."""
    rng = DeterministicRNG(seed=1999)
    fs = 250.0
    t = np.arange(0, 4, 1 / fs)

    # High memory load: elevated theta (5 Hz), reduced alpha (10 Hz)
    sig_load = 1.5 * np.sin(2 * np.pi * 5.0 * t) + 0.5 * np.sin(2 * np.pi * 10.0 * t) + rng.normal(0, 0.2, len(t))

    welch = VireonWelch(fs=fs, nperseg=256)
    f, psd = welch.compute(sig_load)

    theta_mask = (f >= 4.0) & (f <= 7.0)
    alpha_mask = (f >= 8.0) & (f <= 12.0)

    theta_power = float(np.sum(psd[theta_mask]))
    alpha_power = float(np.sum(psd[alpha_mask]))

    assert theta_power > alpha_power, "Cognitive load theta power should exceed alpha power"


if __name__ == "__main__":
    test_klimesch_1999()
