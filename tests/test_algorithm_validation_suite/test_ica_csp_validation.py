"""ICA and CSP validation against sklearn and MNE.

ICA Tests:
1. Recovers sources (subspace match via SVD > 0.9)
2. Mixing matrix shape matches (n_features, n_components)
3. Reconstruction error < 0.01
4. Deterministic output

CSP Tests:
1. Features correlate > 0.9 with MNE CSP (permutation-matched)
2. Features are log-variance (not raw projections)
3. n_components parameter respected (produces 2*n components)
"""
import numpy as np
import pytest
from numpy.linalg import svd
from itertools import permutations

import sys, os
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
for pkg in ['vireon-core', 'vireon-methods']:
    pkg_path = os.path.join(repo_root, pkg)
    if pkg_path not in sys.path:
        sys.path.insert(0, pkg_path)

from vireon_methods.spatial.vireon_ica import VireonICA
from vireon_methods.machine_learning.csp import CSPPlugin
from mne.decoding import CSP as MNE_CSP


@pytest.fixture
def mixed_signals():
    """Generate 3 independent non-Gaussian sources, mixed into 6 channels."""
    rng = np.random.default_rng(42)
    n_samples = 5000
    # Non-Gaussian sources (Laplacian, uniform, bimodal)
    s1 = rng.laplace(0, 1, n_samples)
    s2 = rng.uniform(-2, 2, n_samples)
    s3 = np.concatenate([rng.normal(-3, 0.5, n_samples // 2), rng.normal(3, 0.5, n_samples // 2)])
    S = np.vstack([s1, s2, s3]).T  # (n_samples, 3)
    # Random mixing matrix (6 sensors, 3 sources)
    A = rng.normal(0, 1, (6, 3))
    X = S @ A.T  # (n_samples, 6)
    return X, S, A


# ===== ICA Tests =====

def test_ica_recovers_sources(mixed_signals):
    """ICA should recover sources matching true sources subspace (SVD > 0.9)."""
    X, S_true, _ = mixed_signals
    ica = VireonICA(n_components=3)
    S_v = ica.fit_transform(X)
    # Check subspace alignment via SVD of correlation matrix
    cross_corr = np.corrcoef(S_v.T, S_true.T)[:3, 3:]
    _, sv, _ = svd(np.abs(cross_corr))
    min_sv = float(np.min(sv))
    assert min_sv > 0.9, f"ICA subspace match {min_sv:.3f} < 0.9"


def test_ica_mixing_matrix_shape(mixed_signals):
    """ICA mixing matrix must have shape (n_features, n_components)."""
    X, _, _ = mixed_signals
    ica = VireonICA(n_components=3).fit(X)
    assert ica.mixing_.shape == (6, 3), f"Mixing matrix shape {ica.mixing_.shape}, expected (6, 3)"


def test_ica_reconstruction_error(mixed_signals):
    """X ≈ S @ mixing.T + mean should have low reconstruction error (< 0.01)."""
    X, _, _ = mixed_signals
    ica = VireonICA(n_components=3).fit(X)
    S = ica.transform(X)
    X_reconstructed = S @ ica.mixing_.T + ica.mean_
    error = np.linalg.norm(X - X_reconstructed) / np.linalg.norm(X)
    assert error < 0.01, f"Reconstruction error {error:.4f} > 0.01"


def test_ica_deterministic(mixed_signals):
    """VireonICA must produce deterministic decomposition across runs."""
    X, _, _ = mixed_signals
    ica1 = VireonICA(n_components=3)
    S1 = ica1.fit_transform(X)
    ica2 = VireonICA(n_components=3)
    S2 = ica2.fit_transform(X)
    assert np.allclose(S1, S2), "VireonICA output must be deterministic"


def test_ica_matches_sklearn_fastica(mixed_signals):
    """VireonICA output subspace must match sklearn.decomposition.FastICA with SVD > 0.95."""
    try:
        from sklearn.decomposition import FastICA
    except ImportError:
        pytest.skip("sklearn not available")

    X, _, _ = mixed_signals
    v_ica = VireonICA(n_components=3).fit(X)
    S_v = v_ica.transform(X)

    sk_ica = FastICA(n_components=3, random_state=42).fit(X)
    S_sk = sk_ica.transform(X)

    cross_corr = np.corrcoef(S_v.T, S_sk.T)[:3, 3:]
    _, sv, _ = svd(np.abs(cross_corr))
    min_sv = float(np.min(sv))
    assert min_sv > 0.95, f"VireonICA vs sklearn FastICA subspace match {min_sv:.4f} <= 0.95"


# ===== CSP Tests =====

@pytest.fixture
def eeg_data():
    """Generate synthetic EEG with class-discriminable spatial patterns."""
    rng = np.random.default_rng(42)
    n_epochs, n_channels, n_samples = 40, 8, 250
    X = np.zeros((n_epochs, n_channels, n_samples))
    y = np.array([0, 1] * (n_epochs // 2))
    for i in range(n_epochs):
        noise = rng.normal(0, 1, (n_channels, n_samples))
        if y[i] == 0:
            # Class 0: high variance in channels 0-3
            noise[:4] *= 3.0
        else:
            # Class 1: high variance in channels 4-7
            noise[4:] *= 3.0
        X[i] = noise
    return X, y


def test_csp_features_match_mne(eeg_data):
    """CSPPlugin features should correlate > 0.9 with MNE CSP features (permutation-matched)."""
    X, y = eeg_data
    csp_v = CSPPlugin(n_components=2)
    feats_v = csp_v.execute({"signal": X, "labels": y})
    # MNE CSP with n_components=4 yields 4 components (2 top + 2 bottom)
    csp_m = MNE_CSP(n_components=4, reg=None, log=True, norm_trace=False)
    feats_m = csp_m.fit_transform(X, y)

    # Permutation matching
    best_corr = 0.0
    for perm in permutations(range(feats_v.shape[1])):
        corr = np.corrcoef(feats_v[:, list(perm)].flatten(), feats_m.flatten())[0, 1]
        best_corr = max(best_corr, abs(corr))
    assert best_corr > 0.9, f"CSP feature correlation {best_corr:.3f} < 0.9"


def test_csp_log_variance_features(eeg_data):
    """CSP features must be log-variance (not raw projections)."""
    X, y = eeg_data
    csp = CSPPlugin(n_components=2)
    features = csp.execute({"signal": X, "labels": y})
    assert np.all(features < 10), "Features look like raw projections, not log-variance"
    assert np.all(features > -50), "Features have extreme negative values"


def test_csp_n_components_respected(eeg_data):
    """n_components parameter must control output feature count (2*n_components)."""
    X, y = eeg_data
    for n in [1, 2, 3]:
        csp = CSPPlugin(n_components=n)
        features = csp.execute({"signal": X, "labels": y})
        assert features.shape[1] == 2 * n, (
            f"n_components={n} gave {features.shape[1]} features, expected {2*n}"
        )
