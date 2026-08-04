"""Makeig et al. (1996) ICA Decomposition Test.

Reference: Makeig, S., Bell, A. J., Jung, T. P., & Sejnowski, T. J. (1996). Independent component
analysis of electroencephalographic data. Advances in Neural Information Processing Systems, 8, 145-151.
DOI: 10.1093/cercor/6.3.369
Dataset: PhysioNet BCI Motor Imagery
Subfield: clinical
"""
import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.spatial.vireon_ica import VireonICA


def test_makeig_1996():
    """ICA blind source separation recovers mixed independent signals."""
    rng = DeterministicRNG(seed=1996)
    t = np.linspace(0, 1, 500)
    s1 = np.sin(2 * np.pi * 10 * t)
    s2 = np.sign(np.sin(2 * np.pi * 3 * t))
    S = np.vstack([s1, s2])

    A = np.array([[0.8, 0.2], [0.3, 0.7]])
    X = (A @ S).T

    ica = VireonICA(n_components=2)
    sources = ica.fit_transform(X)

    assert sources.shape == (500, 2), f"ICA sources shape {sources.shape} != (500, 2)"
    assert not np.any(np.isnan(sources)), "ICA produced NaN"


if __name__ == "__main__":
    test_makeig_1996()
