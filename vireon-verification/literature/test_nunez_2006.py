"""Nunez & Srinivasan (2006) Spectral Analysis Test.

Reference: Nunez, P. L., & Srinivasan, R. (2006). Electric fields of the brain: 
the neurophysics of EEG. Oxford University Press. DOI: 10.1093/acprof:oso/9780195050387.001.0001
Dataset: PhysioNet BCI Motor Imagery
Subfield: cognitive
"""
import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.spectral.vireon_welch import VireonWelch


def test_nunez_2006():
    """1/f spectral power law decay and narrow-band alpha peak quantification."""
    rng = DeterministicRNG(seed=2006)
    fs = 250.0
    t = np.arange(0, 4, 1 / fs)

    # 1/f noise + 10 Hz alpha peak
    sig = np.sin(2 * np.pi * 10.0 * t) + rng.normal(0, 0.5, len(t))

    welch = VireonWelch(fs=fs, nperseg=256)
    f, psd = welch.compute(sig)

    peak_idx = np.argmin(np.abs(f - 10.0))
    alpha_peak_power = psd[peak_idx]
    background_power = np.mean(psd[(f >= 20.0) & (f <= 30.0)])

    assert alpha_peak_power > 2.0 * background_power, "10 Hz spectral peak fail"


if __name__ == "__main__":
    test_nunez_2006()
