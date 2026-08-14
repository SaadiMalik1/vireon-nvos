"""Rivet et al. (2009) xDAWN ERP Enhancement Literature Test.

Reference: Rivet, B., Cecotti, H., Souloumiac, A., Maby, E., & Mattout, J. (2009). xDAWN algorithm to enhance evoked potentials: application to brain-computer interfaces. IEEE Transactions on Biomedical Engineering, 56(8), 2035-2043.
DOI: 10.1109/TBME.2009.2019709
"""
import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.spatial.vireon_xdawn import VireonxDAWN


def test_rivet_2009():
    rng = DeterministicRNG(seed=2009)
    n_epochs, n_channels, n_samples = 30, 8, 250
    X = rng.normal(0, 1.0, (n_epochs, n_channels, n_samples))
    y = np.array([0, 1] * (n_epochs // 2))

    xdawn = VireonxDAWN(n_filter=2)
    xdawn.fit(X, y)
    proj = xdawn.transform(X)
    assert proj.shape == (30, 2, 250)


if __name__ == "__main__":
    test_rivet_2009()
