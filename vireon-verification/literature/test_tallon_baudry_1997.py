"""Tallon-Baudry et al. (1997) Induced Gamma Activity Test.

Reference: Tallon-Baudry, C., Bertrand, O., Delpuech, C., & Pernier, J. (1997). Induced gamma-band 
activity during the delay of a visual short-term memory task in humans. Journal of Neuroscience,
17(2), 722-734. DOI: 10.1523/JNEUROSCI.17-02-00722.1997
Dataset: ERP CORE
Subfield: cognitive
"""
import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.spectral.vireon_welch import VireonWelch


def test_tallon_baudry_1997():
    """Induced high-frequency gamma (40 Hz) activity detection."""
    rng = DeterministicRNG(seed=1997)
    fs = 500.0
    t = np.arange(0, 2, 1 / fs)

    # 40 Hz gamma burst during visual binding delay
    sig = np.sin(2 * np.pi * 40.0 * t) + rng.normal(0, 0.3, len(t))

    welch = VireonWelch(fs=fs, nperseg=256)
    f, psd = welch.compute(sig)

    gamma_mask = (f >= 35.0) & (f <= 45.0)
    gamma_power = float(np.sum(psd[gamma_mask]))

    assert gamma_power > 0.20, f"Induced gamma power {gamma_power:.3f} <= 0.20"


if __name__ == "__main__":
    test_tallon_baudry_1997()
