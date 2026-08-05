"""Lawhern et al. (2018) EEGNet Literature Test.

Reference: Lawhern, V. J., Solon, A. J., Waytowich, N. R., Gordon, S. M., Hung, T. M., & Lance, B. J. (2018).
EEGNet: a compact convolutional neural network for EEG-based brain-computer interfaces. Journal of Neural Engineering, 15(5), 056013.
DOI: 10.1088/1741-2552/aace8c
"""
import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.deep_learning.eegnet import EEGNetWrapper


def test_lawhern_2018():
    rng = DeterministicRNG(seed=2018)
    n_epochs, n_channels, n_samples = 40, 8, 250
    X = rng.normal(0, 1.0, (n_epochs, n_channels, n_samples))
    y = np.array([0, 1] * (n_epochs // 2))

    net = EEGNetWrapper(n_classes=2, channels=8, samples=250)
    net.fit(X, y)
    preds = net.predict(X)
    assert len(preds) == n_epochs


if __name__ == "__main__":
    test_lawhern_2018()
