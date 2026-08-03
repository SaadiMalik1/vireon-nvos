"""Beamforming and source localization validation.

LCMV Tests:
1. Localizes known single source to correct leadfield index
2. Output shape matches (n_sources, n_samples)
3. Stable with regularization on rank-deficient data
4. Deterministic output

MNE Inverse Tests:
1. Localizes known single source to correct leadfield index
2. Uses lambda2 = 1 / snr^2 regularization parameter
3. Output shape matches (n_sources, n_samples)
4. Deterministic output
"""
import numpy as np
import pytest

import sys, os
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
for pkg in ['vireon-core', 'vireon-methods']:
    pkg_path = os.path.join(repo_root, pkg)
    if pkg_path not in sys.path:
        sys.path.insert(0, pkg_path)

from vireon_methods.source_localization.vireon_beamforming import VireonLCMV
from vireon_methods.source_localization.vireon_source_localization import VireonMinimumNorm


@pytest.fixture
def forward_setup():
    """Create a simple forward model with known source locations."""
    n_sensors, n_sources = 8, 10
    rng = np.random.default_rng(42)
    # Random leadfield (n_sensors, n_sources)
    L = rng.normal(0, 1, (n_sensors, n_sources))
    # Known source at index 3
    true_source_idx = 3
    # Source time course (10 Hz sine)
    n_samples = 100
    fs = 100.0
    t = np.arange(n_samples) / fs
    source_tc = np.sin(2 * np.pi * 10 * t)
    # Simulated sensor data
    X = np.outer(L[:, true_source_idx], source_tc)  # (n_sensors, n_samples)
    # Add small noise
    X += rng.normal(0, 0.01, X.shape)
    return L, X, true_source_idx, n_sources


# ===== LCMV Tests =====

def test_lcmv_localizes_known_source(forward_setup):
    """LCMV should localize the source to the correct index."""
    L, X, true_idx, _ = forward_setup
    lcmv = VireonLCMV(leadfield=L, reg=0.01)
    lcmv.fit(X)
    source_estimate = lcmv.apply(X)
    # Peak activation should be at the true source index
    peak_idx = np.argmax(np.var(source_estimate, axis=1))
    assert peak_idx == true_idx, f"LCMV localized to {peak_idx}, expected {true_idx}"


def test_lcmv_output_shape(forward_setup):
    """LCMV output shape must be (n_sources, n_samples)."""
    L, X, _, n_sources = forward_setup
    lcmv = VireonLCMV(leadfield=L)
    lcmv.fit(X)
    est = lcmv.apply(X)
    assert est.shape == (n_sources, X.shape[1]), (
        f"Shape {est.shape}, expected ({n_sources}, {X.shape[1]})"
    )


def test_lcmv_regularization_stability():
    """LCMV with regularization should not crash or produce NaN on ill-conditioned covariance."""
    rng = np.random.default_rng(42)
    L = rng.normal(0, 1, (4, 5))
    # Rank-deficient data (2 sources, 4 sensors)
    S = rng.normal(0, 1, (2, 100))
    X = L[:, :2] @ S  # rank 2
    lcmv = VireonLCMV(leadfield=L, reg=0.1)  # high regularization
    lcmv.fit(X)
    est = lcmv.apply(X)
    assert est.shape == (5, 100)
    assert not np.any(np.isnan(est)), "LCMV produced NaN with regularization"


def test_lcmv_deterministic(forward_setup):
    """LCMV must produce deterministic source estimates."""
    L, X, _, _ = forward_setup
    lcmv1 = VireonLCMV(leadfield=L, reg=0.01).fit(X)
    est1 = lcmv1.apply(X)
    lcmv2 = VireonLCMV(leadfield=L, reg=0.01).fit(X)
    est2 = lcmv2.apply(X)
    assert np.array_equal(est1, est2), "LCMV estimates not deterministic"


# ===== MNE Inverse Tests =====

def test_mne_localizes_known_source(forward_setup):
    """MNE inverse should localize the source to the correct index."""
    L, X, true_idx, _ = forward_setup
    mne = VireonMinimumNorm(leadfield=L, snr=3.0)
    est = mne.fit(X)
    peak_idx = np.argmax(np.var(est, axis=1))
    assert peak_idx == true_idx, f"MNE localized to {peak_idx}, expected {true_idx}"


def test_mne_uses_lambda2(forward_setup):
    """MNE must use lambda2 = 1/snr^2 in the inverse."""
    L, X, _, _ = forward_setup
    mne = VireonMinimumNorm(leadfield=L, snr=3.0)
    assert abs(mne.lambda2 - 1.0 / 9.0) < 1e-10, (
        f"lambda2={mne.lambda2}, expected {1.0/9.0:.4f}"
    )


def test_mne_output_shape(forward_setup):
    """MNE output shape must be (n_sources, n_samples)."""
    L, X, _, n_sources = forward_setup
    mne = VireonMinimumNorm(leadfield=L, snr=3.0)
    est = mne.fit(X)
    assert est.shape == (n_sources, X.shape[1]), (
        f"Shape {est.shape}, expected ({n_sources}, {X.shape[1]})"
    )


def test_mne_deterministic(forward_setup):
    """MNE inverse must produce deterministic source estimates."""
    L, X, _, _ = forward_setup
    mne1 = VireonMinimumNorm(leadfield=L, snr=3.0)
    est1 = mne1.fit(X)
    mne2 = VireonMinimumNorm(leadfield=L, snr=3.0)
    est2 = mne2.fit(X)
    assert np.array_equal(est1, est2), "MNE estimates not deterministic"
