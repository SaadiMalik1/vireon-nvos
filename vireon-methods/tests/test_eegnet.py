import numpy as np
import pytest
from vireon_methods.deep_learning.eegnet import EEGNetWrapper, EEGNetPyTorch


def test_eegnet_pytorch_forward_shape():
    """Verify PyTorch EEGNet forward pass output shape."""
    pytest.importorskip("torch")
    import torch

    model = EEGNetPyTorch(n_classes=2, channels=8, samples=250)
    x = torch.randn(10, 1, 8, 250)
    out = model(x)
    assert out.shape == (10, 2)


def test_eegnet_wrapper_fit_predict():
    """Verify EEGNetWrapper fit and predict pipeline."""
    rng = np.random.default_rng(42)
    X = rng.normal(0, 1.0, (20, 8, 250))
    y = np.array([0, 1] * 10)

    net = EEGNetWrapper(n_classes=2, channels=8, samples=250, epochs=2, seed=42)
    net.fit(X, y)
    preds = net.predict(X)
    assert preds.shape == (20,)
    assert set(preds).issubset({0, 1})


def test_eegnet_uses_gpu_when_available():
    """Verify EEGNet model is on CUDA when GPU is available."""
    pytest.importorskip("torch")
    import torch
    if not torch.cuda.is_available():
        pytest.skip("No GPU available")
    net = EEGNetWrapper(use_gpu=True, channels=8, samples=250)
    net.fit(np.random.randn(20, 8, 250).astype(np.float32),
            np.array([0] * 10 + [1] * 10))
    assert next(net.model.parameters()).is_cuda, "Model should be on CUDA"
