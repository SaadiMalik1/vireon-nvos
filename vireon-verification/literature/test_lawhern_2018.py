"""Lawhern et al. (2018) EEGNet Literature Test.

Reference: Lawhern, V. J., Solon, A. J., Waytowich, N. R., Gordon, S. M., Hung, T. M., & Lance, B. J. (2018).
EEGNet: a compact convolutional neural network for EEG-based brain-computer interfaces. Journal of Neural Engineering, 15(5), 056013.
DOI: 10.1088/1741-2552/aace8c
"""
import numpy as np
import pytest
from vireon_methods.deep_learning.eegnet import EEGNetWrapper


def test_lawhern_2018_eegnet_accuracy():
    """Reproduce Lawhern 2018 EEGNet: accuracy > 0.60 on synthetic binary task."""
    pytest.importorskip("torch")

    rng = np.random.default_rng(2018)
    n_epochs, n_channels, n_samples = 60, 8, 250
    t = np.arange(n_samples) / 250.0
    X = np.zeros((n_epochs, n_channels, n_samples))
    y = np.zeros(n_epochs, dtype=int)
    # Class 0: 10 Hz
    X[:30] = np.sin(2 * np.pi * 10 * t)[None, None, :] + rng.normal(0, 0.1, (30, n_channels, n_samples))
    # Class 1: 20 Hz
    X[30:] = np.sin(2 * np.pi * 20 * t)[None, None, :] + rng.normal(0, 0.1, (30, n_channels, n_samples))
    y[30:] = 1

    net = EEGNetWrapper(n_classes=2, channels=n_channels, samples=n_samples, epochs=20, seed=2018)
    net.fit(X, y)
    preds = net.predict(X)

    acc = float((preds == y).mean())
    assert acc > 0.60, f"EEGNet train accuracy {acc:.3f} below 0.60 threshold"
    assert len(preds) == n_epochs


def test_lawhern_2018_eegnet_deterministic():
    """Same seed -> same predictions (PyTorch determinism)."""
    pytest.importorskip("torch")

    rng = np.random.default_rng(2018)
    X = rng.normal(0, 1.0, (40, 8, 250))
    y = np.array([0] * 20 + [1] * 20)

    net1 = EEGNetWrapper(n_classes=2, channels=8, samples=250, epochs=5, seed=2018)
    net1.fit(X, y)
    preds1 = net1.predict(X)

    net2 = EEGNetWrapper(n_classes=2, channels=8, samples=250, epochs=5, seed=2018)
    net2.fit(X, y)
    preds2 = net2.predict(X)

    assert np.array_equal(preds1, preds2), "Same seed must produce identical predictions"


if __name__ == "__main__":
    test_lawhern_2018_eegnet_accuracy()
    test_lawhern_2018_eegnet_deterministic()
