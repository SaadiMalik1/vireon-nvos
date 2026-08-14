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

    # Inject a class-discriminative spatial pattern (different channel
    # scaling per class) so the CSP eigenvalue problem has a real signal.
    for i in range(n_epochs):
        if y[i] == 0:
            X[i, 0] *= 4.0
            X[i, 1] *= 0.5
        else:
            X[i, 6] *= 4.0
            X[i, 7] *= 0.5

    csp = VireonCSP(n_components=4)
    feats = csp.fit_transform(X, y)
    assert feats.shape == (30, 4)

    # Strengthened falsifiable assertion: CSP features must show non-trivial
    # variance (no degenerate projection) AND support above-chance
    # classification. CSP is reviewed in Lotte 2018 as the canonical
    # spatial-filtering method for BCI; a correct implementation should
    # produce class-discriminative log-variance features.
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
    test_lotte_2018()
