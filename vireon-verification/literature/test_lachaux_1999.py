"""Reproduce Lachaux 1999: Wavelet Coherence Phase Synchrony in Brain Signals.

Reference: Lachaux, J. P., Rodriguez, E., Martinerie, J., & Varela, F. J. (1999).
Measuring phase synchrony in brain signals. Human Brain Mapping, 8(4), 194-208.
DOI: 10.1002/(SICI)1097-0193(1999)8:4<194::AID-HBM4>3.0.CO;2-C
"""
import numpy as np
import pytest
from vireon_methods.connectivity.vireon_wavelet_coherence import VireonWaveletCoherence


def test_lachaux_wavelet_coherence_identical_signals():
    """Wavelet coherence between identical signals should equal 1.0."""
    fs = 250.0
    t = np.linspace(0, 2, 500)
    sig = np.sin(2 * np.pi * 10 * t) + np.sin(2 * np.pi * 20 * t)
    data = np.vstack([sig, sig])
    
    wc = VireonWaveletCoherence()
    coh = wc.compute(data, fs=fs)
    
    assert coh[0, 1] > 0.95, f"Expected wavelet coherence > 0.95 for identical signals, got {coh[0, 1]:.4f}"


def test_lachaux_wavelet_coherence_uncorrelated_noise():
    """Wavelet coherence between uncorrelated random noise signals should be low (< 0.5)."""
    fs = 250.0
    np.random.seed(42)
    sig1 = np.random.randn(500)
    sig2 = np.random.randn(500)
    data = np.vstack([sig1, sig2])
    
    wc = VireonWaveletCoherence()
    coh = wc.compute(data, fs=fs)
    
    assert coh[0, 1] < 0.50, f"Expected wavelet coherence < 0.50 for independent noise, got {coh[0, 1]:.4f}"
