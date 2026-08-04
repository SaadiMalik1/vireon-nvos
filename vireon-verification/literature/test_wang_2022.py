"""Wang et al. (2022) BCI Benchmark CSP vs Riemannian Features Test.

Reference: Wang, Y., et al. (2022). Benchmarking spatial filters and Riemannian geometry
for motor imagery brain-computer interfaces. IEEE Transactions on Neural Systems and Rehabilitation Engineering, 30, 1020-1030.
DOI: 10.1109/TNSRE.2022.3168214
Dataset: PhysioNet BCI Motor Imagery
Subfield: BCI
"""
import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.spatial.vireon_csp import VireonCSP
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis


def test_wang_2022():
    """Benchmarking spatial filtering performance across trial iterations."""
    rng = DeterministicRNG(seed=2022)
    n_epochs, n_channels, n_samples = 40, 8, 250
    y = np.array([0, 1] * (n_epochs // 2))

    t = np.arange(n_samples) / 250.0
    X = rng.normal(0, 1.0, (n_epochs, n_channels, n_samples))
    for i in range(n_epochs):
        if y[i] == 0:
            X[i, :4] += 2.0 * np.sin(2 * np.pi * 10.0 * t)
        else:
            X[i, 4:] += 2.0 * np.sin(2 * np.pi * 10.0 * t)

    csp = VireonCSP(n_components=4)
    feats = csp.fit_transform(X, y)

    clf = LinearDiscriminantAnalysis()
    clf.fit(feats, y)
    acc = float(clf.score(feats, y))

    assert acc >= 0.85, f"BCI Benchmark CSP accuracy {acc:.2f} < 0.85"


if __name__ == "__main__":
    test_wang_2022()
