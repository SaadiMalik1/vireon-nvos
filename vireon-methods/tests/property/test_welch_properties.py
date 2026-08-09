from hypothesis import given, strategies as st, assume
import numpy as np
from vireon_methods.spectral.vireon_welch import VireonWelch


@given(
    fs=st.integers(200, 1000),
    nperseg=st.integers(256, 1024),
    n_samples=st.integers(2000, 10000),
    freq=st.floats(5, 50),
)
def test_welch_recovers_known_frequency(fs, nperseg, n_samples, freq):
    """Welch PSD should recover a known sinusoid frequency within frequency resolution."""
    assume(freq < fs / 2)  # Below Nyquist
    assume(nperseg <= n_samples)
    df = fs / nperseg
    assume(df <= 2.0)  # Adequate frequency resolution
    t = np.arange(n_samples) / fs
    signal = np.sin(2 * np.pi * freq * t)
    f, psd = VireonWelch(fs=fs, nperseg=nperseg).compute(signal)
    peak_idx = np.argmax(psd)
    peak_freq = f[peak_idx]
    assert abs(peak_freq - freq) <= df + 1e-5, f"Expected {freq} Hz within {df} Hz resolution, got {peak_freq} Hz"


@given(
    fs=st.integers(100, 500),
    nperseg=st.integers(64, 256),
    n_samples=st.integers(500, 2000),
)
def test_welch_psd_non_negative(fs, nperseg, n_samples):
    """Welch PSD values must always be non-negative."""
    assume(nperseg <= n_samples)
    signal = np.random.default_rng(42).normal(size=n_samples)
    f, psd = VireonWelch(fs=fs, nperseg=nperseg).compute(signal)
    assert np.all(psd >= 0.0)
