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


def test_blankertz_2008_fbcsp_accuracy():
    """Reproduce Blankertz 2008 FBCSP result: accuracy > 0.70 on synthetic multi-band data."""
    from vireon_methods.spatial.vireon_fbcsp import VireonFBCSP
    rng = np.random.default_rng(2008)
    fs = 250.0
    n_epochs, n_channels, n_samples = 60, 22, 1000
    t = np.arange(n_samples) / fs

    X = np.zeros((n_epochs, n_channels, n_samples))
    y = np.zeros(n_epochs, dtype=int)
    # Construct class-discriminative multi-band signal
    for i in range(30):
        X[i, :8] += np.sin(2 * np.pi * 11 * t)
        X[i, 14:] += np.sin(2 * np.pi * 24 * t)
        y[i] = 0
    for i in range(30, 60):
        X[i, 8:14] += np.sin(2 * np.pi * 11 * t)
        X[i, :8] += np.sin(2 * np.pi * 24 * t)
        y[i] = 1
    X += rng.normal(0, 0.1, X.shape)

    fbcsp = VireonFBCSP(bands=[(8.0, 14.0), (20.0, 28.0)], n_components=3)
    feats = fbcsp.fit_transform(X, y, fs=fs)

    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
    from sklearn.model_selection import cross_val_score
    acc = float(cross_val_score(LinearDiscriminantAnalysis(), feats, y, cv=5).mean())
    assert acc > 0.70, f"FBCSP accuracy {acc:.3f} below 0.70 threshold"


if __name__ == "__main__":
    test_blankertz_2008()
    test_blankertz_2008_fbcsp_accuracy()
