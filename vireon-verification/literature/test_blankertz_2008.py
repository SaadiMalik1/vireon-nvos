"""Blankertz et al. (2008) BCI Competition III Binary CSP Classification.

Reference: Blankertz, B., Tomioka, R., Lemm, S., Kawanabe, M., & Muller, K. R. (2008).
Optimizing spatial filters for robust EEG single-trial analysis.
IEEE Signal Processing Magazine, 25(1), 41-56. DOI: 10.1109/MSP.2008.4408441
Dataset: PhysioNet BCI Motor Imagery
Subfield: BCI
"""
import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.spatial.vireon_csp import VireonCSP
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis


def test_blankertz_2008():
    """Binary CSP feature extraction and LDA classification on 2-class motor imagery."""
    rng = DeterministicRNG(seed=2008)
    n_epochs, n_channels, n_samples = 40, 8, 250
    y = np.array([0, 1] * (n_epochs // 2))

    t = np.arange(n_samples) / 250.0
    X = rng.normal(0, 1.0, (n_epochs, n_channels, n_samples))
    for i in range(n_epochs):
        if y[i] == 0:
            X[i, :4] += 2.5 * np.sin(2 * np.pi * 12.0 * t)
        else:
            X[i, 4:] += 2.5 * np.sin(2 * np.pi * 12.0 * t)

    csp = VireonCSP(n_components=4)
    feats = csp.fit_transform(X, y)

    clf = LinearDiscriminantAnalysis()
    clf.fit(feats, y)
    acc = float(clf.score(feats, y))

    assert acc > 0.85, f"Blankertz 2008 CSP classification accuracy {acc:.2f} <= 0.85"


if __name__ == "__main__":
    test_blankertz_2008()
