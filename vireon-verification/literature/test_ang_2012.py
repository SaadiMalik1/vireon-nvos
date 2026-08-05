"""Ang et al. (2012) Filter Bank CSP (FBCSP) Literature Test.

Reference: Ang, K. K., Chin, Z. Y., Zhang, H., & Guan, C. (2012). Filter bank common spatial pattern (FBCSP) in brain-computer interface. IEEE IJCNN, 2390-2397.
DOI: 10.1109/IJCNN.2012.6252486
"""
import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.spatial.vireon_fbcsp import VireonFBCSP


def test_ang_2012():
    rng = DeterministicRNG(seed=2012)
    n_epochs, n_channels, n_samples = 30, 6, 250
    X = rng.normal(0, 1.0, (n_epochs, n_channels, n_samples))
    y = np.array([0, 1] * (n_epochs // 2))

    fbcsp = VireonFBCSP(n_components=2)
    feats = fbcsp.fit_transform(X, y)
    assert feats.shape == (30, 10)


if __name__ == "__main__":
    test_ang_2012()
