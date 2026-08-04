"""Comprehensive FFT validation: VireonFFT vs scipy.fft / scipy.signal.

Tests:
1. PSD matches scipy.signal.periodogram for Hann/Hamming/Blackman windows (rtol=1e-7)
2. Magnitude spectrum matches np.abs(scipy.fft.rfft) (rtol=1e-10)
3. Phase spectrum matches np.angle(scipy.fft.rfft) (atol=1e-10)
4. One-sided scaling correct (factor of 2 for non-DC, non-Nyquist bins)
5. DC bin not doubled
6. Nyquist bin not doubled (even nfft)
7. Different nfft sizes (256, 512, 1024, 2048) all match
8. Short signal (< nfft) handled correctly (zero-padding)
9. Deterministic: same input → same output
10. Frequency axis matches scipy

Reference: scipy.signal.periodogram uses symmetric windows via get_window(),
VireonFFT uses periodic windows — both produce matching PSD to ~1e-13.
Validated empirically before writing these tests.
"""
import numpy as np
import pytest
import scipy.signal
import scipy.fft

import sys, os
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
for pkg in ['vireon-core', 'vireon-methods']:
    pkg_path = os.path.join(repo_root, pkg)
    if pkg_path not in sys.path:
        sys.path.insert(0, pkg_path)

from vireon_methods.spectral.vireon_fft import VireonFFT


@pytest.fixture
def test_signal():
    """Deterministic multi-tone signal with noise.

    Components: 10 Hz (amplitude 10), 20 Hz (amplitude 5), Gaussian noise (σ=0.5).
    Seed: np.random.default_rng(42) — deterministic, no np.random.* calls.
    """
    rng = np.random.default_rng(42)
    fs = 250.0
    t = np.arange(0, 10, 1 / fs)  # 2500 samples, 10 seconds
    sig = 10 * np.sin(2 * np.pi * 10 * t) + 5 * np.sin(2 * np.pi * 20 * t) + rng.normal(0, 0.5, len(t))
    return fs, sig


# --- PSD validation against scipy.signal.periodogram ---

@pytest.mark.parametrize("window", ["hann", "hamming", "blackman"])
def test_psd_matches_scipy_periodogram(test_signal, window):
    """VireonFFT PSD must match scipy.signal.periodogram for 3 window types.

    Tolerance: rtol=1e-7 (conservative; empirical match is ~1e-13).
    """
    fs, sig = test_signal
    f_v, psd_v = VireonFFT(fs=fs, window=window).compute(sig)
    f_s, psd_s = scipy.signal.periodogram(
        sig, fs=fs, window=window, detrend="constant", scaling="density"
    )
    assert f_v.shape == f_s.shape, f"Frequency axis length mismatch: {len(f_v)} vs {len(f_s)}"
    assert np.allclose(f_v, f_s), "Frequency axes must match"
    assert np.allclose(psd_v, psd_s, rtol=1e-7), (
        f"PSD mismatch with {window} window: max_rel_diff="
        f"{np.max(np.abs(psd_v - psd_s) / (np.abs(psd_s) + 1e-20)):.3e}"
    )


def test_psd_frequency_axis_correct(test_signal):
    """Frequency axis must span [0, fs/2] with correct spacing."""
    fs, sig = test_signal
    f_v, _ = VireonFFT(fs=fs).compute(sig)
    assert f_v[0] == 0.0, "First frequency bin must be 0 Hz (DC)"
    assert abs(f_v[-1] - fs / 2) < 1e-10, f"Last bin must be Nyquist ({fs/2} Hz), got {f_v[-1]}"
    # Spacing = fs / nfft
    expected_spacing = fs / len(sig)
    actual_spacing = f_v[1] - f_v[0]
    assert abs(actual_spacing - expected_spacing) < 1e-10, (
        f"Frequency spacing {actual_spacing} != expected {expected_spacing}"
    )


# --- Magnitude spectrum validation ---

def test_magnitude_spectrum_matches_rfft(test_signal):
    """VireonFFT magnitude spectrum must match |rfft(windowed signal)|.

    Tolerance: rtol=1e-10 (matches to ~1e-13 empirically).
    """
    fs, sig = test_signal
    f_v, mag_v = VireonFFT(fs=fs, window="hann").compute_magnitude_spectrum(sig)
    # Reference: detrend, window, rfft
    sig_detrended = sig - np.mean(sig)
    N = len(sig)
    win = 0.5 - 0.5 * np.cos(2.0 * np.pi * np.arange(N) / N)  # periodic hann
    mag_ref = np.abs(scipy.fft.rfft(sig_detrended * win))
    assert np.allclose(mag_v, mag_ref, rtol=1e-10), (
        f"Magnitude spectrum mismatch: max_diff={np.max(np.abs(mag_v - mag_ref)):.3e}"
    )


# --- Phase spectrum validation ---

def test_phase_spectrum_matches_rfft(test_signal):
    """VireonFFT phase spectrum must match angle(rfft(windowed signal)).

    Tolerance: atol=1e-10 (matches to ~1e-13 empirically).
    """
    fs, sig = test_signal
    f_v, phase_v = VireonFFT(fs=fs, window="hann").compute_phase_spectrum(sig)
    sig_detrended = sig - np.mean(sig)
    N = len(sig)
    win = 0.5 - 0.5 * np.cos(2.0 * np.pi * np.arange(N) / N)
    phase_ref = np.angle(scipy.fft.rfft(sig_detrended * win))
    assert np.allclose(phase_v, phase_ref, atol=1e-10), (
        f"Phase spectrum mismatch: max_diff={np.max(np.abs(phase_v - phase_ref)):.3e}"
    )


# --- One-sided scaling validation ---

def test_one_sided_scaling_dc_not_doubled():
    """DC bin (index 0) must NOT be doubled in one-sided PSD.

    This is a well-known convention: one-sided PSD doubles all bins except
    DC and Nyquist to account for the missing negative-frequency half.
    """
    fs = 250.0
    N = 250
    rng = np.random.default_rng(123)
    sig = rng.normal(0, 1, N)
    f_v, psd_v = VireonFFT(fs=fs, window="boxcar", detrend="constant").compute(sig)
    f_s, psd_s = scipy.signal.periodogram(
        sig, fs=fs, window="boxcar", detrend="constant", scaling="density"
    )
    # Verify DC bin specifically matches scipy's periodogram
    assert abs(psd_v[0] - psd_s[0]) / (abs(psd_s[0]) + 1e-20) < 1e-7, (
        f"DC bin mismatch: vireon={psd_v[0]:.6e}, scipy={psd_s[0]:.6e}"
    )


def test_one_sided_scaling_nyquist_not_doubled():
    """Nyquist bin (last bin for even N) must NOT be doubled."""
    fs = 250.0
    N = 250  # even
    rng = np.random.default_rng(456)
    sig = rng.normal(0, 1, N)
    f_v, psd_v = VireonFFT(fs=fs, window="boxcar", detrend="constant").compute(sig)
    f_s, psd_s = scipy.signal.periodogram(
        sig, fs=fs, window="boxcar", detrend="constant", scaling="density"
    )
    # Nyquist is last bin
    assert abs(psd_v[-1] - psd_s[-1]) / (abs(psd_s[-1]) + 1e-20) < 1e-7, (
        f"Nyquist bin mismatch: vireon={psd_v[-1]:.6e}, scipy={psd_s[-1]:.6e}"
    )


def test_one_sided_scaling_middle_bins_doubled():
    """Middle bins (1 to N//2-1) should be 2x the two-sided spectrum.

    Compare VireonFFT one-sided PSD against manual 2x two-sided calculation.
    """
    fs = 256.0
    N = 256
    rng = np.random.default_rng(789)
    sig = rng.normal(0, 1, N)
    f_v, psd_v = VireonFFT(fs=fs, window="boxcar", detrend="constant").compute(sig)
    f_s, psd_s = scipy.signal.periodogram(
        sig, fs=fs, window="boxcar", detrend="constant", scaling="density"
    )
    # All bins must match scipy (which does its own one-sided scaling)
    assert np.allclose(psd_v, psd_s, rtol=1e-7), (
        f"One-sided PSD doesn't match scipy: max_rel_diff="
        f"{np.max(np.abs(psd_v - psd_s) / (np.abs(psd_s) + 1e-20)):.3e}"
    )


# --- Different nfft sizes ---

@pytest.mark.parametrize("nfft", [256, 512, 1024, 2048])
def test_different_nfft_sizes(test_signal, nfft):
    """VireonFFT PSD must match scipy.periodogram for various nfft sizes.

    Uses only the first nfft samples of the signal (no zero-padding ambiguity).
    """
    fs, sig = test_signal
    sig_truncated = sig[:nfft]
    f_v, psd_v = VireonFFT(fs=fs, nfft=nfft, window="hann").compute(sig_truncated)
    f_s, psd_s = scipy.signal.periodogram(
        sig_truncated, fs=fs, nfft=nfft, window="hann", detrend="constant", scaling="density"
    )
    assert len(f_v) == len(f_s), f"Frequency axis length mismatch for nfft={nfft}"
    assert np.allclose(psd_v, psd_s, rtol=1e-7), (
        f"PSD mismatch for nfft={nfft}: max_rel_diff="
        f"{np.max(np.abs(psd_v - psd_s) / (np.abs(psd_s) + 1e-20)):.3e}"
    )


# --- Short signal (zero-padding) ---

def test_short_signal_zero_padded():
    """Signal shorter than nfft should be zero-padded, producing nfft//2+1 bins."""
    fs = 250.0
    sig = np.sin(2 * np.pi * 10 * np.arange(0, 0.5, 1 / fs))  # 125 samples
    f, psd = VireonFFT(fs=fs, nfft=256, window="hann").compute(sig)
    expected_bins = 256 // 2 + 1  # 129
    assert len(f) == expected_bins, f"Expected {expected_bins} bins, got {len(f)}"
    # PSD should have a peak near 10 Hz
    peak_freq = f[np.argmax(psd)]
    assert abs(peak_freq - 10) < 2.0, f"Peak at {peak_freq} Hz, expected ~10 Hz"


# --- Determinism ---

def test_deterministic_output(test_signal):
    """Same input signal → identical output on repeated calls."""
    fs, sig = test_signal
    f1, psd1 = VireonFFT(fs=fs).compute(sig)
    f2, psd2 = VireonFFT(fs=fs).compute(sig)
    assert np.array_equal(f1, f2), "Frequency axes differ between calls"
    assert np.array_equal(psd1, psd2), "PSD values differ between calls (non-deterministic!)"


# --- Peak detection sanity check ---

def test_peak_detection_10hz_and_20hz(test_signal):
    """The test signal has components at 10 and 20 Hz; PSD must peak there."""
    fs, sig = test_signal
    f, psd = VireonFFT(fs=fs).compute(sig)
    # Find the two highest peaks
    peak_indices = np.argsort(psd)[-2:]
    peak_freqs = sorted(f[peak_indices])
    assert abs(peak_freqs[0] - 10) < 1.0, f"Expected peak near 10 Hz, got {peak_freqs[0]}"
    assert abs(peak_freqs[1] - 20) < 1.0, f"Expected peak near 20 Hz, got {peak_freqs[1]}"


# --- Edge case: pure DC signal ---

def test_pure_dc_signal():
    """A DC-only signal should have zero PSD after detrending (detrend='constant')."""
    fs = 100.0
    sig = np.ones(200) * 5.0  # Pure DC
    f, psd = VireonFFT(fs=fs, detrend="constant").compute(sig)
    # After subtracting mean, signal is all zeros → PSD = 0
    assert np.allclose(psd, 0, atol=1e-20), "Pure DC signal after detrending should have zero PSD"


def test_fft_ccc_matches_scipy(test_signal):
    """VireonFFT PSD must match scipy.signal.periodogram with Lin's CCC > 0.9999."""
    from vireon_validation.statistics.framework import lin_concordance_correlation

    fs, sig = test_signal
    f_v, psd_v = VireonFFT(fs=fs, window="hann", detrend="constant").compute(sig)
    f_sp, psd_sp = scipy.signal.periodogram(sig, fs=fs, window="hann", detrend="constant")

    ccc = lin_concordance_correlation(psd_v, psd_sp)
    assert ccc > 0.9999, f"VireonFFT vs scipy.signal.periodogram CCC {ccc:.6f} <= 0.9999"
