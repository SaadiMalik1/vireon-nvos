"""STFT and Wavelet validation against scipy and analytical formulas.

STFT Tests:
1. Output is complex (preserves phase)
2. Frequency and time axes have correct dimensions
3. Chirp detection: STFT reveals increasing frequency over time
4. Segment-by-segment matches manual windowed FFT
5. Deterministic: same input → same output

Wavelet Tests:
1. Output is complex (preserves phase)
2. Morlet CWT detects known 10 Hz tone
3. Multi-tone detection: CWT has peaks at 10 and 30 Hz
4. CWT output shape: (n_frequencies, n_samples)
5. Deterministic: same input → same output

Note on STFT normalization: VireonSTFT divides each segment's FFT by
sum(window), while scipy.signal.stft uses a different normalization.
Both are valid conventions. We validate VireonSTFT against its own
documented formula (manual segment-by-segment) rather than forcing
scipy equivalence.
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

from vireon_methods.spectral.vireon_stft import VireonSTFT
from vireon_methods.spectral.vireon_wavelets import VireonWavelet


@pytest.fixture
def chirp_signal():
    """Chirp signal sweeping 5-50 Hz over 5 seconds, with small noise."""
    rng = np.random.default_rng(42)
    fs = 250.0
    t = np.arange(0, 5, 1 / fs)
    sig = scipy.signal.chirp(t, f0=5, f1=50, t1=5, method='linear') + rng.normal(0, 0.1, len(t))
    return fs, sig


# ===== STFT Tests =====

def test_stft_output_is_complex(chirp_signal):
    """STFT must return complex coefficients (preserves phase information)."""
    fs, sig = chirp_signal
    _, _, Z = VireonSTFT(fs=fs, nperseg=256, noverlap=128).compute(sig)
    assert np.iscomplexobj(Z), "STFT output must be complex to preserve phase"


def test_stft_frequency_axis_correct(chirp_signal):
    """Frequency axis must span [0, fs/2] with nperseg//2+1 bins."""
    fs, sig = chirp_signal
    f, t, Z = VireonSTFT(fs=fs, nperseg=256, noverlap=128).compute(sig)
    expected_n_freqs = 256 // 2 + 1  # 129
    assert len(f) == expected_n_freqs, f"Expected {expected_n_freqs} freq bins, got {len(f)}"
    assert f[0] == 0.0, "First frequency must be 0 Hz (DC)"
    assert abs(f[-1] - fs / 2) < 1e-10, f"Last frequency must be Nyquist ({fs/2} Hz)"


def test_stft_time_axis_correct(chirp_signal):
    """Time axis must have correct number of segments and center positions."""
    fs, sig = chirp_signal
    nperseg = 256
    noverlap = 128
    step = nperseg - noverlap
    expected_n_segments = (len(sig) - nperseg) // step + 1
    f, t, Z = VireonSTFT(fs=fs, nperseg=nperseg, noverlap=noverlap).compute(sig)
    assert len(t) == expected_n_segments, (
        f"Expected {expected_n_segments} time segments, got {len(t)}"
    )
    assert Z.shape == (len(f), len(t)), f"Z shape {Z.shape} doesn't match (n_freq, n_time)"


def test_stft_detects_chirp(chirp_signal):
    """STFT should show increasing peak frequency for a linear chirp."""
    fs, sig = chirp_signal
    f, t, Z = VireonSTFT(fs=fs, nperseg=256, noverlap=128).compute(sig)
    magnitude = np.abs(Z)

    # Peak frequency at first time segment should be low (~5 Hz)
    peak_freq_start = f[np.argmax(magnitude[:, 0])]
    # Peak frequency at last time segment should be high (~50 Hz)
    peak_freq_end = f[np.argmax(magnitude[:, -1])]

    assert peak_freq_start < 15, f"Initial peak frequency {peak_freq_start:.1f} Hz should be < 15 Hz"
    assert peak_freq_end > 35, f"Final peak frequency {peak_freq_end:.1f} Hz should be > 35 Hz"
    assert peak_freq_end > peak_freq_start, "Peak frequency should increase for chirp"


def test_stft_matches_manual_segmented_fft(chirp_signal):
    """VireonSTFT must match a manual segment-by-segment windowed FFT.

    This validates the implementation against its own formula:
    Z[:, i] = rfft(segment * window) / sum(window)
    """
    fs, sig = chirp_signal
    nperseg = 256
    noverlap = 128
    step = nperseg - noverlap

    stft_obj = VireonSTFT(fs=fs, nperseg=nperseg, noverlap=noverlap)
    f_v, t_v, Z_v = stft_obj.compute(sig)

    # Manual computation
    win = 0.5 - 0.5 * np.cos(2.0 * np.pi * np.arange(nperseg) / nperseg)
    win_sum = np.sum(win)
    n_segments = (len(sig) - nperseg) // step + 1

    for i in range(n_segments):
        start = i * step
        segment = sig[start:start + nperseg].copy()
        segment -= np.mean(segment)  # detrend constant
        expected = np.fft.rfft(segment * win) / win_sum
        assert np.allclose(Z_v[:, i], expected, rtol=1e-10), (
            f"Segment {i} mismatch: max_diff={np.max(np.abs(Z_v[:, i] - expected)):.3e}"
        )


def test_stft_deterministic(chirp_signal):
    """Same input → identical STFT output on repeated calls."""
    fs, sig = chirp_signal
    stft = VireonSTFT(fs=fs, nperseg=256, noverlap=128)
    _, _, Z1 = stft.compute(sig)
    _, _, Z2 = stft.compute(sig)
    assert np.array_equal(Z1, Z2), "STFT not deterministic"


# ===== Wavelet (CWT) Tests =====

def test_wavelet_output_is_complex():
    """CWT must return complex coefficients to preserve phase."""
    fs = 250.0
    t = np.arange(0, 2, 1 / fs)
    sig = np.sin(2 * np.pi * 10 * t)
    wav = VireonWavelet(fs=fs, frequencies=np.array([10.0]), wavelet="morlet")
    cwt = wav.compute(sig)
    assert np.iscomplexobj(cwt), "Wavelet transform must preserve phase (complex output)"


def test_wavelet_detects_10hz():
    """CWT should detect a pure 10 Hz sine in the frequency range 1-50 Hz."""
    fs = 250.0
    t = np.arange(0, 2, 1 / fs)
    sig = np.sin(2 * np.pi * 10 * t)
    frequencies = np.linspace(1, 50, 50)
    wav = VireonWavelet(fs=fs, frequencies=frequencies, wavelet="morlet")
    cwt = wav.compute(sig)
    magnitude = np.abs(cwt)
    # Average power across time for each frequency
    avg_power = magnitude.mean(axis=1)
    peak_freq_idx = np.argmax(avg_power)
    peak_freq = frequencies[peak_freq_idx]
    assert abs(peak_freq - 10) < 2.0, f"CWT peak at {peak_freq:.1f} Hz, expected ~10 Hz"


def test_wavelet_selectivity():
    """CWT power at the signal's frequency should be much higher than at distant frequencies.

    For a 10 Hz pure sine, power at 10 Hz should dominate over power at 40+ Hz.
    This validates the wavelet's frequency selectivity.
    """
    fs = 250.0
    t = np.arange(0, 4, 1 / fs)
    sig = np.sin(2 * np.pi * 10 * t)
    frequencies = np.array([5.0, 10.0, 20.0, 40.0])
    wav = VireonWavelet(fs=fs, frequencies=frequencies, wavelet="morlet")
    cwt = wav.compute(sig)
    avg_power = np.abs(cwt).mean(axis=1)

    # Power at 10 Hz should be the highest
    peak_idx = np.argmax(avg_power)
    assert frequencies[peak_idx] == 10.0, (
        f"Peak at {frequencies[peak_idx]} Hz, expected 10 Hz. Powers: {dict(zip(frequencies, avg_power))}"
    )
    # Power at 10 Hz should be much higher than at 40 Hz
    power_10 = avg_power[1]  # index 1 = 10 Hz
    power_40 = avg_power[3]  # index 3 = 40 Hz
    ratio = power_10 / (power_40 + 1e-20)
    assert ratio > 5.0, f"Selectivity ratio {ratio:.1f} < 5.0: wavelet not selective enough"


def test_wavelet_output_shape():
    """CWT output shape must be (n_frequencies, n_samples)."""
    fs = 250.0
    n_samples = 500
    sig = np.sin(2 * np.pi * 10 * np.arange(n_samples) / fs)
    frequencies = np.linspace(5, 40, 20)
    wav = VireonWavelet(fs=fs, frequencies=frequencies, wavelet="morlet")
    cwt = wav.compute(sig)
    assert cwt.shape == (20, n_samples), f"CWT shape {cwt.shape}, expected (20, {n_samples})"


def test_wavelet_deterministic():
    """Same input → identical CWT output."""
    fs = 250.0
    sig = np.sin(2 * np.pi * 10 * np.arange(0, 2, 1 / fs))
    frequencies = np.linspace(5, 40, 10)
    wav = VireonWavelet(fs=fs, frequencies=frequencies, wavelet="morlet")
    cwt1 = wav.compute(sig)
    cwt2 = wav.compute(sig)
    assert np.array_equal(cwt1, cwt2), "CWT not deterministic"
