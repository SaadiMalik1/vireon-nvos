import numpy as np
import pytest
import scipy.signal
from vireon_methods.spectral.vireon_stft import VireonSTFT
from vireon_core.contracts.plugin import ScientificContractViolation

def test_stft_matches_scipy():
    fs = 250
    sig = np.random.default_rng(42).normal(size=5000)
    
    # Vireon
    f_v, t_v, Z_v = VireonSTFT(fs=fs, nperseg=256, noverlap=128).compute(sig)
    
    # Scipy
    f_s, t_s, Z_s = scipy.signal.stft(
        sig, fs=fs, nperseg=256, noverlap=128, 
        window='hann', detrend='constant', boundary=None, padded=False
    )
    
    assert np.allclose(f_v, f_s), "Frequencies must match"
    assert np.allclose(t_v, t_s), "Times must match"
    assert np.allclose(Z_v, Z_s, rtol=1e-7), "STFT complex values must match scipy within 1e-7"

def test_stft_is_complex():
    sig = np.random.default_rng(0).normal(size=1000)
    _, _, Z = VireonSTFT(fs=250, nperseg=256).compute(sig)
    assert np.iscomplexobj(Z), "Output STFT matrix must be complex"
    
def test_stft_rejects_nan():
    sig = np.array([1.0, np.nan, 3.0])
    with pytest.raises((ScientificContractViolation, ValueError)):
        VireonSTFT(fs=250, nperseg=2).compute(sig)

def test_stft_rejects_short_signal():
    sig = np.zeros(100)
    with pytest.raises((ScientificContractViolation, ValueError)):
        VireonSTFT(fs=250, nperseg=256).compute(sig)
