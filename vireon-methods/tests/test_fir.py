import numpy as np
import pytest
import scipy.signal
from vireon_methods.filtering.vireon_fir import VireonFIR
from vireon_core.contracts.plugin import ScientificContractViolation

def test_fir_lowpass_matches_scipy():
    coeffs_v = VireonFIR(fs=250, cutoff=40, numtaps=101, pass_zero=True).design()
    coeffs_s = scipy.signal.firwin(101, 40, fs=250, window="hamming", pass_zero=True)
    assert np.allclose(coeffs_v, coeffs_s, rtol=1e-10, atol=1e-10)

def test_fir_highpass_matches_scipy():
    coeffs_v = VireonFIR(fs=250, cutoff=10, numtaps=101, pass_zero=False).design()
    coeffs_s = scipy.signal.firwin(101, 10, fs=250, window="hamming", pass_zero=False)
    assert np.allclose(coeffs_v, coeffs_s, rtol=1e-10, atol=1e-10)

def test_fir_bandpass_matches_scipy():
    coeffs_v = VireonFIR(fs=250, cutoff=(10, 40), numtaps=101, pass_zero=False).design()
    coeffs_s = scipy.signal.firwin(101, [10, 40], fs=250, window="hamming", pass_zero=False)
    assert np.allclose(coeffs_v, coeffs_s, rtol=1e-10, atol=1e-10)

def test_fir_bandstop_matches_scipy():
    coeffs_v = VireonFIR(fs=250, cutoff=(10, 40), numtaps=101, pass_zero=True).design()
    coeffs_s = scipy.signal.firwin(101, [10, 40], fs=250, window="hamming", pass_zero=True)
    assert np.allclose(coeffs_v, coeffs_s, rtol=1e-10, atol=1e-10)

def test_fir_apply_matches_scipy():
    sig = np.random.default_rng(42).normal(size=1000)
    fir = VireonFIR(fs=250, cutoff=40, numtaps=101, pass_zero=True)
    filtered_v = fir.apply(sig)
    filtered_s = scipy.signal.filtfilt(fir.coeffs, [1.0], sig)
    assert np.allclose(filtered_v, filtered_s, rtol=1e-7, atol=1e-7)

def test_fir_rejects_nan():
    sig = np.array([1.0, np.nan, 3.0])
    fir = VireonFIR(fs=250, cutoff=40)
    with pytest.raises(ScientificContractViolation):
        fir.apply(sig)
        
def test_fir_rejects_even_numtaps_highpass():
    with pytest.raises(ValueError, match="even number of coefficients"):
        VireonFIR(fs=250, cutoff=10, numtaps=100, pass_zero=False)
