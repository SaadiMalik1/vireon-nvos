import numpy as np
import pytest
from vireon_methods.spectral.vireon_wavelets import VireonWavelet
from vireon_core.contracts.plugin import ScientificContractViolation

def test_wavelet_morlet_peak():
    fs = 250
    sig = np.sin(2 * np.pi * 10 * np.arange(0, 2, 1/fs))
    
    freqs = np.array([5.0, 10.0, 15.0])
    cwt = VireonWavelet(fs=fs, frequencies=freqs, wavelet="morlet").compute(sig)
    
    assert np.iscomplexobj(cwt), "Output must be complex for phase preservation"
    assert cwt.shape == (3, len(sig))
    
    # At center of signal, the peak frequency should be 10Hz (index 1)
    magnitudes = np.abs(cwt[:, len(sig)//2])
    assert np.argmax(magnitudes) == 1, "Peak frequency should be at 10Hz"

def test_wavelet_supports_multiple_wavelets():
    fs = 250
    sig = np.sin(2 * np.pi * 10 * np.arange(0, 1, 1/fs))
    freqs = np.array([10.0])
    
    for wav in ["morlet", "paul", "dog", "mexh"]:
        cwt = VireonWavelet(fs=fs, frequencies=freqs, wavelet=wav).compute(sig)
        assert cwt.shape == (1, len(sig))
        if wav in ["paul", "morlet"]:
            assert np.iscomplexobj(cwt), f"{wav} should be complex"

def test_wavelet_rejects_nan():
    sig = np.array([1.0, np.nan, 3.0])
    with pytest.raises((ScientificContractViolation, ValueError)):
        VireonWavelet(fs=250, frequencies=np.array([10.0])).compute(sig)
