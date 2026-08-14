"""Barachant et al. (2012) Riemannian Geometry Literature Test.

Reference: Barachant, A., Bonnet, S., Congedo, M., & Jutten, C. (2012). Multiclass brain-computer interface classification by Riemannian geometry. IEEE Transactions on Biomedical Engineering, 59(4), 920-928.
DOI: 10.1109/TBME.2011.2172216
"""
import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.spatial.vireon_riemannian import VireonRiemannianMDM


def test_barachant_2012():
    rng = DeterministicRNG(seed=2012)
    n_epochs, n_channels, n_samples = 20, 4, 250
    X = rng.normal(0, 1.0, (n_epochs, n_channels, n_samples))
    y = np.array([0, 1] * (n_epochs // 2))

    mdm = VireonRiemannianMDM()
    preds = mdm.fit_transform(X, y)
    assert len(preds) == n_epochs


if __name__ == "__main__":
    test_barachant_2012()
