"""Reproduce Welch 1967: averaging modified periodograms reduces variance.

Key claim (Welch 1967, §III): The variance of the PSD estimate decreases
as 1/K where K is the number of overlapping segments.

Test:
1. Generate stationary random signals (white noise, known PSD)
2. Compute single-periodogram PSD — high variance
3. Compute Welch PSD with K=8 segments — variance should be ~1/8 of single
4. Verify variance reduction ratio is approximately 1/K
5. Verify recovery of theoretical PSD for white noise (σ²/fs)
6. Verify detection of peak frequency (50 Hz)
7. Generate valid evidence bundle with non-empty cryptographic hash
"""
import os
import sys
import numpy as np
import scipy.signal

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
for pkg in ['vireon-core', 'vireon-methods', 'vireon-validation']:
    pkg_path = os.path.join(repo_root, pkg)
    if pkg_path not in sys.path:
        sys.path.insert(0, pkg_path)

from vireon_methods.spectral.vireon_welch import VireonWelch
from vireon_validation.benchmarks.matrix import BenchmarkMatrix


def test_welch_variance_reduction():
    """Welch PSD variance should be ~1/K of single periodogram variance."""
    rng = np.random.default_rng(42)
    fs = 1000.0
    n_samples = 10000
    n_trials = 100

    single_psd_var = []
    welch_psd_var = []
    for _ in range(n_trials):
        sig = rng.normal(0, 1, n_samples)
        # Single periodogram (K=1)
        f1, psd1 = scipy.signal.periodogram(sig, fs=fs)
        # Welch with K=8 segments (nperseg = n_samples/8, 50% overlap)
        nperseg = n_samples // 8
        f8, psd8 = VireonWelch(fs=fs, nperseg=nperseg, noverlap=nperseg // 2).compute(sig)
        single_psd_var.append(psd1)
        welch_psd_var.append(psd8)

    single_psd_var = np.array(single_psd_var)
    welch_psd_var = np.array(welch_psd_var)

    # Variance across trials at each frequency
    var_single = np.var(single_psd_var, axis=0)
    var_welch = np.var(welch_psd_var, axis=0)

    # Expected: var_welch ≈ var_single / K (K=8)
    # Variance of Welch PSD is reduced relative to single-segment periodogram variance
    ratio = np.mean(var_welch[1:-1]) / np.mean(var_single[1:-1])
    expected_ratio = 1.0 / 8.0

    assert 0.05 < ratio < 0.35, (
        f"Variance ratio {ratio:.4f} not close to 1/K={expected_ratio:.4f}"
    )


def test_welch_recovers_known_psd():
    """Welch one-sided PSD of white noise (σ²=1) should be approximately 2*σ²/fs at all frequencies."""
    rng = np.random.default_rng(42)
    fs = 1000.0
    sig = rng.normal(0, 1, 100000)
    f, psd = VireonWelch(fs=fs, nperseg=1024).compute(sig)
    # For one-sided PSD of white noise with σ²=1, PSD = 2 * σ² / fs = 2 / 1000 = 0.002
    expected_psd = 2.0 / fs
    median_psd = np.median(psd[1:-1])  # exclude DC and Nyquist
    assert abs(median_psd - expected_psd) / expected_psd < 0.1, (
        f"PSD {median_psd:.6f} not within 10% of expected {expected_psd:.6f}"
    )


def test_welch_detects_peak_frequency():
    """Welch PSD should detect a 50 Hz peak in a signal with 50 Hz sine."""
    fs = 1000.0
    t = np.arange(0, 10, 1 / fs)
    sig = np.sin(2 * np.pi * 50 * t) + np.random.default_rng(42).normal(0, 0.1, len(t))
    f, psd = VireonWelch(fs=fs, nperseg=1024).compute(sig)
    peak_idx = np.argmax(psd)
    assert abs(f[peak_idx] - 50) < 1.0, f"Peak at {f[peak_idx]} Hz, expected 50 Hz"


def test_welch_evidence_bundle():
    """Generate an evidence bundle for the Welch reproduction."""
    rng = np.random.default_rng(42)
    fs = 1000.0
    sig = rng.normal(0, 1, 10000)

    class WelchMethod:
        plugin_id = "vk:Method:Spectral:Welch"
        version = "1.0.0"

        def execute(self, inputs):
            f, psd = VireonWelch(fs=fs, nperseg=1024).compute(inputs["signal"].flatten())
            return psd

    matrix = BenchmarkMatrix(seed=42)
    matrix.add_method(WelchMethod())
    matrix.add_dataset("Welch1967_WhiteNoise", data=sig.reshape(1, 1, -1), labels=np.array([0]))
    bundles = matrix.execute_matrix()
    assert len(bundles) > 0
    bundle = bundles[0]
    assert bundle["evidence_hash"] != "", "Evidence hash must be non-empty"
    assert bundle["algorithm"] == "vk:Method:Spectral:Welch"
