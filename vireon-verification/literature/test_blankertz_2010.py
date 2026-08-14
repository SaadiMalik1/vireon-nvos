"""Blankertz et al. (2010) Single-Trial EEG Analysis Literature Test.

Reference: Blankertz, B., et al. (2010). Neuro-technology: Single-trial analysis of EEG signals. NeuroImage, 51(1), 130-140.
DOI: 10.1016/j.neuroimage.2009.04.077
"""
import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.spatial.vireon_csp import VireonCSP


def test_blankertz_2010():
    rng = DeterministicRNG(seed=2010)
    n_epochs, n_channels, n_samples = 30, 8, 250
    X = rng.normal(0, 1.0, (n_epochs, n_channels, n_samples))
    y = np.array([0, 1] * (n_epochs // 2))

    csp = VireonCSP(n_components=2)
    feats = csp.fit_transform(X, y)
    assert feats.shape == (30, 2)


if __name__ == "__main__":
    test_blankertz_2010()
