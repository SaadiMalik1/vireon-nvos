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

    # Inject class-discriminative covariance structure: class 0 epochs have
    # elevated variance on channel 0 (diagonal covariance entry scaled up),
    # class 1 epochs have elevated variance on channel 3. Riemannian MDM
    # operates directly on covariance matrices, so this signal must be
    # learnable by the tangent-space class means.
    for i in range(n_epochs):
        if y[i] == 0:
            X[i, 0] = X[i, 0] * 4.0 + 0.5 * X[i, 1]
        else:
            X[i, 3] = X[i, 3] * 4.0 + 0.5 * X[i, 2]

    mdm = VireonRiemannianMDM()
    preds = mdm.fit_transform(X, y)
    assert len(preds) == n_epochs

    # Strengthened falsifiable assertion: Riemannian MDM must classify above
    # 60% accuracy on class-discriminative covariance structures (above the
    # 50% chance level). The MDM classifier estimates class means on the SPD
    # manifold and assigns each epoch to the nearest mean in Riemannian
    # distance — this should easily separate the two synthetic distributions.
    train_acc = float(np.mean(preds == y))
    assert train_acc > 0.60, (
        f"Riemannian MDM train accuracy {train_acc:.2f} not above 0.60 — "
        "covariance estimation or Riemannian distance computation may be broken"
    )


if __name__ == "__main__":
    test_barachant_2012()
