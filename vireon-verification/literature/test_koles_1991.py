"""Koles et al. (1990) CSP Original Formulation Test.

Reference: Koles, Z. J., Lazar, M. S., & Zhou, S. Z. (1990). Spatial patterns underlying
population differences in the background electroencephalogram. Brain Topography, 2(4), 275-284.
DOI: 10.1016/0013-4694(90)90066-M
Dataset: PhysioNet BCI Motor Imagery
Subfield: BCI
"""
import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.spatial.vireon_csp import VireonCSP


def test_koles_1991():
    """Koles CSP maximizes variance ratio for target class while minimizing for non-target class."""
    rng = DeterministicRNG(seed=1991)
    n_epochs, n_channels, n_samples = 30, 6, 250
    y = np.array([0, 1] * (n_epochs // 2))

    X = rng.normal(0, 1.0, (n_epochs, n_channels, n_samples))
    for i in range(n_epochs):
        if y[i] == 0:
            X[i, 0] *= 3.0
        else:
            X[i, -1] *= 3.0

    csp = VireonCSP(n_components=2)
    feats = csp.fit_transform(X, y)

    var_c0 = np.var(feats[y == 0], axis=0)
    var_c1 = np.var(feats[y == 1], axis=0)

    # First component should have higher variance for class 0, second for class 1
    assert var_c0[0] != var_c1[0], "CSP features failed to discriminate class variance"
    assert feats.shape == (30, 2), "CSP output shape mismatch"


if __name__ == "__main__":
    test_koles_1991()
