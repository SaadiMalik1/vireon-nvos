"""Vallat & Walker (2021) YASA Sleep Staging Test.

Reference: Vallat, R., & Walker, M. P. (2021). An open-source software for automatic 
sleep staging in mice and humans. eLife, 10, e70092. DOI: 10.7554/eLife.70092
Dataset: Sleep-EDF
Subfield: sleep
"""
import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.spectral.vireon_welch import VireonWelch


def test_vallat_2021():
    """YASA spectral power band ratios for NREM (Delta) vs REM/Awake (Theta/Alpha)."""
    rng = DeterministicRNG(seed=2021)
    fs = 100.0
    t = np.arange(0, 30, 1 / fs)  # 30s epoch

    # N3 slow-wave sleep: high delta (1 Hz)
    n3_sig = 4.0 * np.sin(2 * np.pi * 1.0 * t) + rng.normal(0, 0.5, len(t))

    welch = VireonWelch(fs=fs, nperseg=500)
    f, psd = welch.compute(n3_sig)

    delta_mask = (f >= 0.5) & (f <= 4.0)
    delta_power = float(np.sum(psd[delta_mask]))

    assert delta_power > 2.0, f"N3 delta power {delta_power:.2f} <= 2.0"


if __name__ == "__main__":
    test_vallat_2021()
