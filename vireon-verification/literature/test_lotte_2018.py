"""Lotte et al. (2018) BCI Spatial Filtering Review Literature Test.

Reference: Lotte, F., et al. (2018). A review of classification algorithms for EEG-based brain-computer interfaces (2007-2017). Journal of Neural Engineering, 15(3), 031005.
DOI: 10.1088/1741-2552/aab2cd
"""
import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.spatial.vireon_csp import VireonCSP


def test_lotte_2018():
    rng = DeterministicRNG(seed=2018)
    n_epochs, n_channels, n_samples = 30, 8, 250
    X = rng.normal(0, 1.0, (n_epochs, n_channels, n_samples))
    y = np.array([0, 1] * (n_epochs // 2))

    csp = VireonCSP(n_components=4)
    feats = csp.fit_transform(X, y)
    assert feats.shape == (30, 4)


if __name__ == "__main__":
    test_lotte_2018()
