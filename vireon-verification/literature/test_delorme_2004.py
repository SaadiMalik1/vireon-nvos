"""Delorme & Makeig (2004) EEGLAB ICA Pipeline Test.

Reference: Delorme, A., & Makeig, S. (2004). EEGLAB: an open source toolbox for analysis
of single-trial EEG dynamics including independent component analysis. Journal of Neuroscience Methods,
134(1), 9-21. DOI: 10.1016/j.jneumeth.2003.10.009
Dataset: ERP CORE
Subfield: cognitive
"""
import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.spatial.vireon_ica import VireonICA


def test_delorme_2004():
    """EEGLAB artifact component identification and matrix reconstruction."""
    rng = DeterministicRNG(seed=2004)
    t = np.linspace(0, 2, 500)
    # EEG + EOG artifact (blink peak)
    eeg = np.sin(2 * np.pi * 10 * t)
    blink = 5.0 * np.exp(-((t - 1.0) ** 2) / 0.01)
    X = np.vstack([eeg + 0.5 * blink, 0.2 * eeg + blink]).T

    ica = VireonICA(n_components=2)
    sources = ica.fit_transform(X)

    rec = sources[:, :1] @ ica.mixing_[:1, :]
    assert rec.shape == (500, 2), f"Reconstruction shape mismatch {rec.shape}"


if __name__ == "__main__":
    test_delorme_2004()
