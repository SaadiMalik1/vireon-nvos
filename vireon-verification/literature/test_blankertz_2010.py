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

    # Inject a class-discriminative spatial covariance pattern so CSP has a
    # real signal to optimize: class 0 epochs scale channel 0, class 1
    # epochs scale channel 7. CSP's generalized eigenvalue problem should
    # find spatial filters that separate the two covariance structures.
    for i in range(n_epochs):
        if y[i] == 0:
            X[i, 0] *= 4.0
        else:
            X[i, -1] *= 4.0

    csp = VireonCSP(n_components=2)
    feats = csp.fit_transform(X, y)
    assert feats.shape == (30, 2)

    # Strengthened falsifiable assertion: CSP features must show non-trivial
    # variance (the spatial filter must actually project data, not collapse
    # to a constant) and must support above-chance classification.
    feat_var = float(np.var(feats))
    assert feat_var > 1e-6, (
        f"CSP feature variance {feat_var:.2e} not > 0 — "
        "spatial filters collapsed to degenerate projection"
    )

    # CSP+nearest-centroid train accuracy must exceed 60% (above chance).
    classes = np.unique(y)
    centroids = {int(c): feats[y == c].mean(axis=0) for c in classes}
    preds = np.array([
        int(min(centroids, key=lambda c: np.linalg.norm(f - centroids[c])))
        for f in feats
    ])
    train_acc = float(np.mean(preds == y))
    assert train_acc > 0.60, (
        f"CSP+centroid train accuracy {train_acc:.2f} not above 0.60 — "
        "CSP failed to produce class-discriminative log-variance features"
    )


if __name__ == "__main__":
    test_blankertz_2010()
