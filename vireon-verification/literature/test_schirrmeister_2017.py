"""Schirrmeister et al. (2017) DeepConvNet Literature Test.

Reference: Schirrmeister, R. T., et al. (2017). Deep learning with convolutional neural networks for EEG decoding and visualization. Human Brain Mapping, 38(11), 5391-5420.
DOI: 10.1002/hbm.23730
"""
import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.deep_learning.deepconvnet import DeepConvNetWrapper


def test_schirrmeister_2017():
    rng = DeterministicRNG(seed=2017)
    n_epochs, n_channels, n_samples = 40, 8, 250
    X = rng.normal(0, 1.0, (n_epochs, n_channels, n_samples))
    y = np.array([0, 1] * (n_epochs // 2))

    net = DeepConvNetWrapper(n_classes=2, channels=8, samples=250)
    net.fit(X, y)
    preds = net.predict(X)
    assert len(preds) == n_epochs


if __name__ == "__main__":
    test_schirrmeister_2017()
