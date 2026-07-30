import pytest
import numpy as np
from hypothesis import given, settings, strategies as st
from hypothesis.extra.numpy import arrays

from vireon_validation.metrics import compute_snr_raw

# Generate 1D floating point arrays for testing
signal_strategy = arrays(
    dtype=np.float32,
    shape=st.integers(min_value=10, max_value=1000),
    elements=st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False)
)

noise_strategy = arrays(
    dtype=np.float32,
    shape=st.integers(min_value=10, max_value=1000),
    elements=st.floats(min_value=-10.0, max_value=10.0, allow_nan=False, allow_infinity=False)
)

@settings(max_examples=50, deadline=None)
@given(signal=signal_strategy, scale=st.floats(min_value=0.1, max_value=10.0))
def test_snr_scale_invariance(signal, scale):
    """
    Property: SNR is invariant to scalar multiplication (scaling).
    """
    # Exclude all-zero signals to avoid log10(0)
    if np.allclose(signal, 0):
        return
        
    snr_original = compute_snr_raw(signal)
    snr_scaled = compute_snr_raw(signal * scale)
    
    assert abs(snr_original - snr_scaled) < 1e-4

@settings(max_examples=50, deadline=None)
@given(signal=signal_strategy, shift=st.floats(min_value=-100.0, max_value=100.0))
def test_snr_translation_invariance(signal, shift):
    """
    Property: SNR is invariant to DC offset (translation) when DC is removed.
    But since our compute_snr_raw expects zero-mean or computes var,
    SNR = Var(signal) / Var(noise). Translation shouldn't change Variance.
    """
    if np.allclose(signal, 0):
        return
        
    snr_original = compute_snr_raw(signal)
    snr_shifted = compute_snr_raw(signal + shift)
    
    # Variance is shift invariant, so SNR should be shift invariant
    assert abs(snr_original - snr_shifted) < 1e-3
