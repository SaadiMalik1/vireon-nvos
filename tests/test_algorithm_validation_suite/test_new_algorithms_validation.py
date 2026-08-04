"""Validation tests for Multitaper, EMD, and Convolution/Correlation."""
import numpy as np
import pytest
import scipy.signal

from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.spectral.vireon_multitaper import VireonMultitaper
from vireon_methods.time_frequency.vireon_emd import VireonEMD
from vireon_methods.signal_processing.vireon_convolution import VireonConvolution
from vireon_validation.statistics.framework import lin_concordance_correlation


def test_multitaper_psd_matches_reference():
    """Multitaper PSD should detect known frequencies and match scipy DPSS tapers."""
    fs = 250.0
    t = np.arange(0, 4, 1 / fs)
    sig = np.sin(2 * np.pi * 10 * t) + 0.5 * np.sin(2 * np.pi * 30 * t)

    mt = VireonMultitaper(fs=fs, NW=2.5, n_tapers=4)
    f, psd = mt.compute(sig)

    idx10 = np.argmin(np.abs(f - 10.0))
    idx30 = np.argmin(np.abs(f - 30.0))

    peak10_freq = f[idx10 - 2 + np.argmax(psd[idx10 - 2 : idx10 + 3])]
    peak30_freq = f[idx30 - 2 + np.argmax(psd[idx30 - 2 : idx30 + 3])]

    assert abs(peak10_freq - 10) < 1.0, f"Expected peak near 10 Hz, got {peak10_freq}"
    assert abs(peak30_freq - 30) < 1.0, f"Expected peak near 30 Hz, got {peak30_freq}"


def test_emd_reconstructs_original_signal():
    """Sum of EMD IMFs plus residue must equal original signal."""
    rng = DeterministicRNG(seed=123)
    t = np.linspace(0, 1, 300)
    sig = np.sin(2 * np.pi * 5 * t) + np.sin(2 * np.pi * 25 * t) + rng.normal(0, 0.1, 300)

    emd = VireonEMD(max_imfs=4)
    imfs = emd.fit_transform(sig)

    reconstructed = np.sum(imfs, axis=0)
    max_diff = float(np.max(np.abs(sig - reconstructed)))
    assert max_diff < 1e-10, f"EMD reconstruction error {max_diff:.3e} > 1e-10"


def test_convolution_matches_numpy_and_scipy_fftconvolve():
    """VireonConvolution convolve and correlate must match scipy.signal.fftconvolve with Lin's CCC > 0.9999."""
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])
    h = np.array([0.5, 1.0, 0.5])

    conv = VireonConvolution(mode="full")
    y_conv = conv.convolve(x, h)
    y_sp_conv = scipy.signal.fftconvolve(x, h, mode="full")

    ccc_conv = lin_concordance_correlation(y_conv, y_sp_conv)
    assert ccc_conv > 0.9999, f"Convolve vs scipy.signal.fftconvolve CCC {ccc_conv:.6f} <= 0.9999"

    y_corr = conv.correlate(x, h)
    y_np_corr = np.correlate(x, h, mode="full")

    ccc_corr = lin_concordance_correlation(y_corr, y_np_corr)
    assert ccc_corr > 0.9999, f"Correlate CCC {ccc_corr:.6f} <= 0.9999"
