"""FIR and IIR filter validation against scipy.signal.

FIR Tests:
1. Coefficients match scipy.signal.firwin for lowpass/highpass/bandpass/bandstop (rtol=1e-10)
2. FIR lowpass attenuates stopband by > 20 dB
3. Deterministic: same input → same output

IIR Tests:
1. Coefficients match scipy.signal.butter for lowpass/highpass/bandpass/bandstop (rtol=1e-10)
2. Zero-phase filtering matches scipy.signal.filtfilt (rtol=1e-7)
3. IIR filter is stable (all poles inside unit circle)
4. IIR lowpass attenuates stopband by > 20 dB

Reference: scipy.signal.firwin and scipy.signal.butter
"""
import numpy as np
import pytest
import scipy.signal

import sys, os
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
for pkg in ['vireon-core', 'vireon-methods']:
    pkg_path = os.path.join(repo_root, pkg)
    if pkg_path not in sys.path:
        sys.path.insert(0, pkg_path)

from vireon_methods.filtering.vireon_fir import VireonFIR
from vireon_methods.filtering.vireon_iir import VireonIIR


@pytest.fixture
def test_signal():
    """Signal with 10 Hz and 60 Hz components + noise."""
    rng = np.random.default_rng(42)
    fs = 250.0
    t = np.arange(0, 5, 1 / fs)
    sig = np.sin(2 * np.pi * 10 * t) + np.sin(2 * np.pi * 60 * t) + rng.normal(0, 0.1, len(t))
    return fs, sig


# ===== FIR Tests =====

@pytest.mark.parametrize("cutoff,pass_zero,label", [
    (40.0, True, "lowpass"),
    (40.0, False, "highpass"),
    ((30.0, 50.0), False, "bandpass"),
    ((45.0, 55.0), True, "bandstop"),
])
def test_fir_coeffs_match_scipy(cutoff, pass_zero, label):
    """FIR coefficients must match scipy.signal.firwin to machine precision.

    Tolerance: rtol=1e-10 (empirically matches to ~1e-16).
    """
    fs = 250.0
    numtaps = 101
    fir_v = VireonFIR(fs=fs, cutoff=cutoff, numtaps=numtaps, window="hamming", pass_zero=pass_zero)
    coeffs_s = scipy.signal.firwin(numtaps, cutoff, fs=fs, window="hamming", pass_zero=pass_zero)
    assert np.allclose(fir_v.coeffs, coeffs_s, rtol=1e-10, atol=1e-12), (
        f"FIR coefficients mismatch for {label}: "
        f"max_diff={np.max(np.abs(fir_v.coeffs - coeffs_s)):.3e}"
    )


def test_fir_attenuates_stopband(test_signal):
    """FIR lowpass at 40 Hz must attenuate 60 Hz by > 20 dB."""
    fs, sig = test_signal
    filt = VireonFIR(fs=fs, cutoff=40.0, numtaps=101, pass_zero=True)
    filtered = filt.apply(sig)
    f, psd_before = scipy.signal.welch(sig, fs=fs, nperseg=512)
    f, psd_after = scipy.signal.welch(filtered, fs=fs, nperseg=512)
    idx_60 = np.argmin(np.abs(f - 60))
    attenuation_db = 10 * np.log10(psd_after[idx_60] / (psd_before[idx_60] + 1e-30))
    assert attenuation_db < -20, (
        f"60 Hz attenuation only {attenuation_db:.1f} dB, need < -20 dB"
    )


def test_fir_preserves_passband(test_signal):
    """FIR lowpass at 40 Hz must preserve 10 Hz signal (< 3 dB loss)."""
    fs, sig = test_signal
    filt = VireonFIR(fs=fs, cutoff=40.0, numtaps=101, pass_zero=True)
    filtered = filt.apply(sig)
    f, psd_before = scipy.signal.welch(sig, fs=fs, nperseg=512)
    f, psd_after = scipy.signal.welch(filtered, fs=fs, nperseg=512)
    idx_10 = np.argmin(np.abs(f - 10))
    loss_db = 10 * np.log10(psd_after[idx_10] / (psd_before[idx_10] + 1e-30))
    assert loss_db > -3, f"10 Hz passband loss {loss_db:.1f} dB, should be > -3 dB"


def test_fir_deterministic(test_signal):
    """FIR filter must produce identical output for identical input."""
    fs, sig = test_signal
    filt = VireonFIR(fs=fs, cutoff=40.0, numtaps=101, pass_zero=True)
    out1 = filt.apply(sig)
    out2 = filt.apply(sig)
    assert np.array_equal(out1, out2), "FIR filter not deterministic"


# ===== IIR Tests =====

@pytest.mark.parametrize("btype,cutoff", [
    ("lowpass", 40.0),
    ("highpass", 40.0),
    ("bandpass", (30.0, 50.0)),
    ("bandstop", (45.0, 55.0)),
])
def test_iir_coeffs_match_scipy(btype, cutoff):
    """IIR coefficients must match scipy.signal.butter to machine precision.

    Tolerance: rtol=1e-10 (empirically matches to ~1e-16).
    """
    fs = 250.0
    iir = VireonIIR(fs=fs, cutoff=cutoff, btype=btype, order=4, filter_type="butter")
    b_s, a_s = scipy.signal.butter(4, cutoff, fs=fs, btype=btype)
    assert np.allclose(iir.b, b_s, rtol=1e-10), (
        f"IIR b coefficients mismatch for {btype}: "
        f"max_diff={np.max(np.abs(iir.b - b_s)):.3e}"
    )
    assert np.allclose(iir.a, a_s, rtol=1e-10), (
        f"IIR a coefficients mismatch for {btype}: "
        f"max_diff={np.max(np.abs(iir.a - a_s)):.3e}"
    )


def test_iir_zero_phase_matches_filtfilt(test_signal):
    """IIR zero-phase filtering must match scipy.signal.filtfilt."""
    fs, sig = test_signal
    iir = VireonIIR(fs=fs, cutoff=40.0, btype="lowpass", order=4)
    filtered_v = iir.apply(sig, zero_phase=True)
    filtered_s = scipy.signal.filtfilt(iir.b, iir.a, sig)
    assert np.allclose(filtered_v, filtered_s, rtol=1e-7), (
        f"Zero-phase filtering mismatch: "
        f"max_diff={np.max(np.abs(filtered_v - filtered_s)):.3e}"
    )


def test_iir_filter_stability():
    """IIR filter must be stable: all poles inside unit circle."""
    iir = VireonIIR(fs=250.0, cutoff=40.0, btype="lowpass", order=8)
    poles = np.roots(iir.a)
    max_pole_mag = np.max(np.abs(poles))
    assert max_pole_mag < 1.0 - 1e-6, (
        f"IIR filter has unstable poles: max |pole| = {max_pole_mag:.8f}"
    )


def test_iir_attenuates_stopband(test_signal):
    """IIR lowpass at 40 Hz must attenuate 60 Hz by > 20 dB."""
    fs, sig = test_signal
    iir = VireonIIR(fs=fs, cutoff=40.0, btype="lowpass", order=4)
    filtered = iir.apply(sig, zero_phase=True)
    f, psd_before = scipy.signal.welch(sig, fs=fs, nperseg=512)
    f, psd_after = scipy.signal.welch(filtered, fs=fs, nperseg=512)
    idx_60 = np.argmin(np.abs(f - 60))
    attenuation_db = 10 * np.log10(psd_after[idx_60] / (psd_before[idx_60] + 1e-30))
    assert attenuation_db < -20, (
        f"60 Hz attenuation only {attenuation_db:.1f} dB, need < -20 dB"
    )


def test_high_order_iir_sos_stability():
    """High-order IIR filter must remain numerically stable without NaN/Inf."""
    iir = VireonIIR(fs=500.0, cutoff=[1.0, 40.0], btype="bandpass", order=6)
    sig = np.sin(2 * np.pi * 10 * np.linspace(0, 2, 1000))
    filtered = iir.apply(sig, zero_phase=True)
    assert not np.any(np.isnan(filtered)), "High-order IIR filter produced NaN"
    assert not np.any(np.isinf(filtered)), "High-order IIR filter produced Inf"
    assert np.max(np.abs(filtered)) < 5.0, "High-order IIR filter blew up"
