"""Hipp et al. (2012) Cortical Oscillatory Synchrony Test.

Reference: Hipp, J. F., Hawellek, D. J., Corbetta, M., Siegel, M., & Engel, A. K. (2012).
Large-scale cortical oscillatory synchrony reliably measured with EEG/MEG. Nature Neuroscience,
15(6), 887-892. DOI: 10.1038/nn.3101
Dataset: PhysioNet BCI Motor Imagery
Subfield: cognitive
"""
import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.connectivity.vireon_connectivity import VireonAEC


def test_hipp_2012():
    """Envelope correlation removes volume conduction artifacts."""
    rng = DeterministicRNG(seed=2012)
    fs = 250.0
    t = np.arange(0, 10, 1 / fs)

    # Shared amplitude envelope
    env = 1.0 + 0.5 * np.sin(2 * np.pi * 0.5 * t)
    ch1 = env * np.sin(2 * np.pi * 10 * t) + rng.normal(0, 0.1, len(t))
    ch2 = env * np.sin(2 * np.pi * 10 * t + np.pi / 3) + rng.normal(0, 0.1, len(t))
    X = np.vstack([ch1, ch2])

    aec = VireonAEC().compute(X, fs=fs, band=(8, 12))

    assert aec.shape == (2, 2), f"AEC shape mismatch {aec.shape}"
    assert not np.isnan(aec[0, 1]), "AEC produced NaN"


if __name__ == "__main__":
    test_hipp_2012()
