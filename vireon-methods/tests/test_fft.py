import numpy as np
import pytest
import scipy.signal
from vireon_methods.spectral.vireon_fft import VireonFFT
from vireon_core.contracts.plugin import ScientificContractViolation

def test_fft_matches_scipy_periodogram():
    fs = 250
    # Add a fixed seed to be reproducible
    rng = np.random.default_rng(42)
    sig = rng.normal(size=2048)
    
    # scipy's default window is "boxcar", but test requires "hann"
    f_v, psd_v = VireonFFT(fs=fs, window="hann").compute(sig)
    
    # In scipy 1.5.0+, `window='hann'` uses sym=True by default for periodogram? 
    # Actually for periodogram it might use sym=False too because periodogram 
    # uses _spectral_helper.
    # We will test against scipy.signal.periodogram
    f_s, psd_s = scipy.signal.periodogram(sig, fs=fs, window="hann", detrend="constant", scaling="density")
    
    assert np.allclose(f_v, f_s), "Frequencies must match"
    assert np.allclose(psd_v, psd_s, rtol=1e-7), "PSD must match scipy within 1e-7"

def test_magnitude_spectrum_linear():
    sig = np.sin(2*np.pi*10*np.arange(0, 1, 1/250))
    f, mag = VireonFFT(fs=250).compute_magnitude_spectrum(sig)
    peak_idx = np.argmax(mag)
    assert abs(f[peak_idx] - 10) < 1

def test_phase_spectrum_range():
    sig = np.sin(2*np.pi*10*np.arange(0, 1, 1/250))
    f, phase = VireonFFT(fs=250).compute_phase_spectrum(sig)
    assert np.all(phase >= -np.pi - 1e-10)
    assert np.all(phase <= np.pi + 1e-10)

def test_fft_rejects_nan():
    sig = np.array([1.0, np.nan, 3.0])
    with pytest.raises((ScientificContractViolation, ValueError)):
        VireonFFT(fs=250).compute(sig)
