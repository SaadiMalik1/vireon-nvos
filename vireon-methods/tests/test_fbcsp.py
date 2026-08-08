import numpy as np
import pytest
from vireon_methods.spatial.vireon_fbcsp import VireonFBCSP
from vireon_methods.spatial.vireon_csp import VireonCSP


def test_fbcsp_applies_band_specific_filters():
    """Verify each band produces different features (i.e., filtering actually happens)."""
    rng = np.random.default_rng(42)
    fs = 250.0
    n_epochs, n_channels, n_samples = 40, 8, 500
    t = np.arange(n_samples) / fs

    X = np.zeros((n_epochs, n_channels, n_samples))
    y = np.zeros(n_epochs, dtype=int)
    # Class 0: 10 Hz signal
    X[:20] = rng.normal(0, 0.1, (20, n_channels, n_samples)) + np.sin(2 * np.pi * 10 * t)[None, None, :]
    y[:20] = 0
    # Class 1: 25 Hz signal
    X[20:] = rng.normal(0, 0.1, (20, n_channels, n_samples)) + np.sin(2 * np.pi * 25 * t)[None, None, :]
    y[20:] = 1

    bands = [(8.0, 12.0), (22.0, 28.0)]
    fbcsp = VireonFBCSP(bands=bands, n_components=2)
    feats = fbcsp.fit_transform(X, y, fs=fs)

    # Features must have shape (epochs, n_bands * n_components)
    assert feats.shape == (n_epochs, 4), f"Expected (40, 4), got {feats.shape}"

    # Features from different bands must differ (proves filtering happens)
    band0_feats = feats[:, :2]
    band1_feats = feats[:, 2:]
    assert not np.allclose(band0_feats, band1_feats), \
        "FBCSP features identical across bands — filtering not applied!"


def test_fbcsp_fit_transform_separate_calls():
    """Verify fit then transform matches fit_transform."""
    rng = np.random.default_rng(123)
    fs = 250.0
    X = rng.normal(0, 1.0, (20, 4, 250))
    y = np.array([0, 1] * 10)

    fbcsp1 = VireonFBCSP(n_components=2)
    feats1 = fbcsp1.fit_transform(X, y, fs=fs)

    fbcsp2 = VireonFBCSP(n_components=2)
    fbcsp2.fit(X, y, fs=fs)
    feats2 = fbcsp2.transform(X)

    assert np.allclose(feats1, feats2), "fit_transform must match fit + transform"
