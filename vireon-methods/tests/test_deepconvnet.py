import numpy as np
import pytest
from vireon_methods.deep_learning.deepconvnet import DeepConvNetWrapper, DeepConvNetPyTorch


def test_deepconvnet_pytorch_forward_shape():
    """Verify PyTorch DeepConvNet forward pass output shape."""
    pytest.importorskip("torch")
    import torch

    model = DeepConvNetPyTorch(n_classes=2, channels=8, samples=250)
    x = torch.randn(10, 1, 8, 250)
    out = model(x)
    assert out.shape == (10, 2)


def test_deepconvnet_wrapper_fit_predict():
    """Verify DeepConvNetWrapper fit and predict pipeline."""
    rng = np.random.default_rng(42)
    X = rng.normal(0, 1.0, (20, 8, 250))
    y = np.array([0, 1] * 10)

    net = DeepConvNetWrapper(n_classes=2, channels=8, samples=250, epochs=2, seed=42)
    net.fit(X, y)
    preds = net.predict(X)
    assert preds.shape == (20,)
    assert set(preds).issubset({0, 1})
