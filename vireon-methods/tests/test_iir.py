import numpy as np
import pytest
import scipy.signal
from vireon_methods.filtering.vireon_iir import VireonIIR
from vireon_core.contracts.plugin import ScientificContractViolation

def test_iir_lowpass_matches_scipy():
    b_v, a_v = VireonIIR(fs=250, cutoff=40, btype="lowpass", order=4).design()
    b_s, a_s = scipy.signal.butter(4, 40, fs=250, btype="lowpass")
    assert np.allclose(b_v, b_s, rtol=1e-10, atol=1e-10)
    assert np.allclose(a_v, a_s, rtol=1e-10, atol=1e-10)

def test_iir_highpass_matches_scipy():
    b_v, a_v = VireonIIR(fs=250, cutoff=10, btype="highpass", order=4).design()
    b_s, a_s = scipy.signal.butter(4, 10, fs=250, btype="highpass")
    assert np.allclose(b_v, b_s, rtol=1e-10, atol=1e-10)
    assert np.allclose(a_v, a_s, rtol=1e-10, atol=1e-10)

def test_iir_bandpass_matches_scipy():
    b_v, a_v = VireonIIR(fs=250, cutoff=(10, 40), btype="bandpass", order=2).design()
    b_s, a_s = scipy.signal.butter(2, [10, 40], fs=250, btype="bandpass")
    assert np.allclose(b_v, b_s, rtol=1e-10, atol=1e-10)
    assert np.allclose(a_v, a_s, rtol=1e-10, atol=1e-10)

def test_iir_bandstop_matches_scipy():
    b_v, a_v = VireonIIR(fs=250, cutoff=(40, 60), btype="bandstop", order=2).design()
    b_s, a_s = scipy.signal.butter(2, [40, 60], fs=250, btype="bandstop")
    assert np.allclose(b_v, b_s, rtol=1e-10, atol=1e-10)
    assert np.allclose(a_v, a_s, rtol=1e-10, atol=1e-10)

def test_iir_apply_matches_scipy():
    sig = np.random.default_rng(42).normal(size=1000)
    iir = VireonIIR(fs=250, cutoff=40, btype="lowpass", order=4)
    filtered_v = iir.apply(sig, zero_phase=True)
    filtered_s = scipy.signal.filtfilt(iir.b, iir.a, sig)
    assert np.allclose(filtered_v, filtered_s, rtol=1e-7, atol=1e-7)

def test_iir_rejects_nan():
    sig = np.array([1.0, np.nan, 3.0])
    iir = VireonIIR(fs=250, cutoff=40, btype="lowpass", order=2)
    with pytest.raises(ScientificContractViolation):
        iir.apply(sig)
