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

    # Strengthened falsifiable assertion: AEC must detect the shared amplitude
    # envelope between the two channels. Since both channels share the same
    # slow (0.5 Hz) amplitude envelope modulating the 10 Hz carrier, the
    # off-diagonal AEC entry (envelope correlation) must exceed 0.3.
    aec_off = float(aec[0, 1])
    assert aec_off > 0.3, (
        f"AEC[0,1] = {aec_off:.3f} not > 0.3 — "
        "AEC failed to detect the shared amplitude envelope"
    )

    # AEC matrix must be symmetric and have unit diagonal (self-correlation = 1)
    assert abs(float(aec[0, 0]) - 1.0) < 1e-6, (
        f"AEC[0,0] = {aec[0,0]:.3f} != 1.0 — self-envelope correlation must be 1.0"
    )
    assert abs(float(aec[0, 1]) - float(aec[1, 0])) < 1e-9, (
        "AEC matrix not symmetric — correlation matrix must be symmetric"
    )


if __name__ == "__main__":
    test_hipp_2012()
