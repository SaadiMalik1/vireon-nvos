import numpy as np
import pytest
import scipy.signal
from vireon_methods.spectral.vireon_welch import VireonWelch
from vireon_core.contracts.plugin import ScientificContractViolation

def test_welch_matches_scipy():
    fs = 250
    t = np.arange(0, 10, 1/fs)
    rng = np.random.default_rng(42)
    sig = np.sin(2*np.pi*10*t) + 0.1*rng.normal(size=t.shape)
    f_v, psd_v = VireonWelch(fs=fs, nperseg=512).compute(sig)
    f_s, psd_s = scipy.signal.welch(sig, fs=fs, nperseg=512, window='hann', 
                                     noverlap=256, detrend='constant', scaling='density')
    assert np.allclose(f_v, f_s), "Frequency axes must match"
    assert np.allclose(psd_v, psd_s, rtol=1e-7), "PSD must match scipy within 1e-7"

def test_welch_returns_frequency_axis():
    sig = np.random.default_rng(0).normal(size=1000)
    f, psd = VireonWelch(fs=250, nperseg=256).compute(sig)
    assert len(f) == 129  # 256//2 + 1
    assert f[0] == 0
    assert f[-1] == 125  # Nyquist

def test_welch_detects_10hz_peak():
    fs = 250
    t = np.arange(0, 20, 1/fs)
    sig = np.sin(2*np.pi*10*t)
    f, psd = VireonWelch(fs=fs, nperseg=512).compute(sig)
    peak_idx = np.argmax(psd)
    assert abs(f[peak_idx] - 10.0) < 1.0  # within 1 Hz

def test_welch_rejects_nan():
    sig = np.array([1.0, np.nan, 3.0])
    with pytest.raises((ScientificContractViolation, ValueError)):
        VireonWelch(fs=250, nperseg=2).compute(sig)

def test_welch_rejects_short_signal():
    sig = np.zeros(100)
    with pytest.raises((ScientificContractViolation, ValueError)):
        VireonWelch(fs=250, nperseg=512).compute(sig)
