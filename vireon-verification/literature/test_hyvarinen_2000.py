"""Reproduce Hyvärinen & Oja 2000: FastICA recovers independent sources.

Key claims (Hyvärinen & Oja 2000, DOI: 10.1016/S0893-6080(00)00026-5):
1. FastICA recovers sources that are statistically independent.
2. The recovered components should have maximal non-Gaussianity (kurtosis).
3. The original source subspace and mixing matrix can be accurately estimated.

Test:
1. Create 3 non-Gaussian sources (Laplacian, uniform, bimodal)
2. Mix with a random 6x3 matrix
3. Run VireonICA
4. Verify:
   (a) components are less Gaussian than the mixed data (kurtosis)
   (b) source subspace is recovered (SVD match > 0.9)
   (c) mixing matrix is estimated with reconstruction error < 0.05
   (d) components are uncorrelated (|corr| < 0.1)
   (e) valid evidence bundle is generated
"""
import os
import sys
import numpy as np
import pytest
from scipy import stats
from numpy.linalg import svd

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
for pkg in ['vireon-core', 'vireon-methods', 'vireon-validation']:
    pkg_path = os.path.join(repo_root, pkg)
    if pkg_path not in sys.path:
        sys.path.insert(0, pkg_path)

from vireon_methods.spatial.vireon_ica import VireonICA
from vireon_validation.benchmarks.matrix import BenchmarkMatrix


@pytest.fixture
def mixed_signals():
    rng = np.random.default_rng(42)
    n_samples = 5000
    # Non-Gaussian sources (Hyvärinen requires at most 1 Gaussian)
    s1 = rng.laplace(0, 1, n_samples)  # Laplacian (high kurtosis)
    s2 = rng.uniform(-np.sqrt(3), np.sqrt(3), n_samples)  # Uniform (negative excess kurtosis)
    s3 = np.concatenate([
        rng.normal(-3, 0.5, n_samples // 2),
        rng.normal(3, 0.5, n_samples // 2)  # Bimodal
    ])
    S = np.vstack([s1, s2, s3]).T
    A = rng.normal(0, 1, (6, 3))
    X = S @ A.T
    return X, S, A


def test_ica_recoveries_non_gaussian(mixed_signals):
    """ICA components should be non-Gaussian (higher |kurtosis| than central-limit mixtures)."""
    X, S_true, _ = mixed_signals
    ica = VireonICA(n_components=3)
    S_est = ica.fit_transform(X)

    # Mixed data tends toward Gaussian by Central Limit Theorem
    mixed_kurtosis = [abs(stats.kurtosis(X[:, i])) for i in range(X.shape[1])]
    # Estimated components should exhibit higher non-Gaussianity
    est_kurtosis = [abs(stats.kurtosis(S_est[:, i])) for i in range(S_est.shape[1])]

    median_mixed = np.median(mixed_kurtosis)
    non_gaussian_count = sum(1 for k in est_kurtosis if k > median_mixed)
    assert non_gaussian_count >= 2, (
        f"Only {non_gaussian_count}/3 components are non-Gaussian"
    )


def test_ica_subspace_recovery(mixed_signals):
    """ICA should recover the source subspace (SVD match > 0.9)."""
    X, S_true, _ = mixed_signals
    ica = VireonICA(n_components=3)
    S_est = ica.fit_transform(X)

    # Cross-correlation between estimated and true sources
    cross_corr = np.corrcoef(S_est.T, S_true.T)[:3, 3:]
    _, sv, _ = svd(np.abs(cross_corr))
    min_sv = float(np.min(sv))
    assert min_sv > 0.9, f"Subspace match {min_sv:.3f} < 0.9"


def test_ica_mixing_matrix_estimated(mixed_signals):
    """ICA should estimate a mixing matrix that reconstructs X."""
    X, _, _ = mixed_signals
    ica = VireonICA(n_components=3).fit(X)
    assert ica.mixing_.shape == (6, 3), f"Mixing matrix shape {ica.mixing_.shape}"

    # Reconstruction: X ≈ S @ mixing.T + mean
    S = ica.transform(X)
    X_recon = S @ ica.mixing_.T + ica.mean_
    recon_error = np.linalg.norm(X - X_recon) / np.linalg.norm(X)
    assert recon_error < 0.05, f"Reconstruction error {recon_error:.4f} > 0.05"


def test_ica_components_uncorrelated(mixed_signals):
    """ICA components should be approximately uncorrelated (orthogonal)."""
    X, _, _ = mixed_signals
    ica = VireonICA(n_components=3)
    S = ica.fit_transform(X)
    corr = np.corrcoef(S.T)
    # Off-diagonal should be near 0
    off_diag = corr[np.triu_indices(3, k=1)]
    assert np.all(np.abs(off_diag) < 0.1), (
        f"Components not uncorrelated: max |corr| = {np.max(np.abs(off_diag)):.4f}"
    )


def test_ica_evidence_bundle(mixed_signals):
    """Generate an evidence bundle for the ICA reproduction."""
    X, _, _ = mixed_signals

    class ICAMethod:
        plugin_id = "vk:Method:Spatial:ICA"
        version = "1.0.0"
        n_components = 3

        def execute(self, inputs):
            sig = inputs["signal"]
            if sig.ndim == 3:
                sig = sig[0]  # take first epoch
            return VireonICA(n_components=3).fit_transform(sig.T).T

    matrix = BenchmarkMatrix(seed=42)
    matrix.add_method(ICAMethod())
    matrix.add_dataset("Hyvarinen2000_Mixed", data=X.T.reshape(1, *X.T.shape), labels=np.array([0]))
    bundles = matrix.execute_matrix()
    assert len(bundles) > 0
    assert bundles[0]["evidence_hash"] != ""
