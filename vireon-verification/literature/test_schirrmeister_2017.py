"""Schirrmeister et al. (2017) DeepConvNet Literature Test.

Reference: Schirrmeister, R. T., et al. (2017). Deep learning with convolutional neural networks for EEG decoding and visualization. Human Brain Mapping, 38(11), 5391-5420.
DOI: 10.1002/hbm.23730
"""
import numpy as np
import pytest
from vireon_methods.deep_learning.deepconvnet import DeepConvNetWrapper


def test_schirrmeister_2017_deepconvnet_accuracy():
    """Reproduce Schirrmeister 2017 DeepConvNet: accuracy > 0.60 on synthetic binary task."""
    pytest.importorskip("torch")

    rng = np.random.default_rng(2017)
    n_epochs, n_channels, n_samples = 60, 8, 250
    t = np.arange(n_samples) / 250.0
    X = np.zeros((n_epochs, n_channels, n_samples))
    y = np.zeros(n_epochs, dtype=int)
    # Class 0: 10 Hz
    X[:30] = np.sin(2 * np.pi * 10 * t)[None, None, :] + rng.normal(0, 0.1, (30, n_channels, n_samples))
    # Class 1: 20 Hz
    X[30:] = np.sin(2 * np.pi * 20 * t)[None, None, :] + rng.normal(0, 0.1, (30, n_channels, n_samples))
    y[30:] = 1

    net = DeepConvNetWrapper(n_classes=2, channels=n_channels, samples=n_samples, epochs=20, seed=2017)
    net.fit(X, y)
    preds = net.predict(X)

    acc = float((preds == y).mean())
    assert acc > 0.60, f"DeepConvNet train accuracy {acc:.3f} below 0.60 threshold"
    assert len(preds) == n_epochs


def test_schirrmeister_2017_deepconvnet_deterministic():
    """Same seed -> same predictions (PyTorch determinism)."""
    pytest.importorskip("torch")

    rng = np.random.default_rng(2017)
    X = rng.normal(0, 1.0, (40, 8, 250))
    y = np.array([0] * 20 + [1] * 20)

    net1 = DeepConvNetWrapper(n_classes=2, channels=8, samples=250, epochs=5, seed=2017)
    net1.fit(X, y)
    preds1 = net1.predict(X)

    net2 = DeepConvNetWrapper(n_classes=2, channels=8, samples=250, epochs=5, seed=2017)
    net2.fit(X, y)
    preds2 = net2.predict(X)

    assert np.array_equal(preds1, preds2), "Same seed must produce identical predictions"


if __name__ == "__main__":
    test_schirrmeister_2017_deepconvnet_accuracy()
    test_schirrmeister_2017_deepconvnet_deterministic()
