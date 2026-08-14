import numpy as np
import pytest
from vireon_methods.connectivity.vireon_connectivity import (
    VireonCoherence, VireonPLV, VireonPLI, VireonAEC, VireonWPLI
)
from vireon_core.contracts.plugin import ScientificContractViolation

def test_coherence():
    rng = np.random.default_rng(42)
    fs = 250
    t = np.arange(0, 4, 1/fs)
    # create two signals, one is a shifted version of another
    x1 = np.sin(2 * np.pi * 10 * t) + rng.normal(scale=0.1, size=len(t))
    x2 = np.sin(2 * np.pi * 10 * t + np.pi/4) + rng.normal(scale=0.1, size=len(t))
    X = np.vstack([x1, x2])
    
    coh = VireonCoherence().compute(X, fs=fs, band=(8, 12))
    assert coh.shape == (2, 2)
    assert np.allclose(coh[0, 1], coh[1, 0])
    assert np.isclose(coh[0, 0], 1.0)
    # high coherence since they are related
    assert coh[0, 1] > 0.5
    
def test_plv_locked():
    fs = 250
    t = np.arange(0, 4, 1/fs)
    x1 = np.sin(2 * np.pi * 10 * t)
    x2 = np.sin(2 * np.pi * 10 * t + np.pi/4)
    X = np.vstack([x1, x2])
    
    plv = VireonPLV().compute(X, fs=fs, band=(8, 12))
    assert np.isclose(plv[0, 0], 1.0)
    assert plv[0, 1] > 0.95
    
def test_plv_noise():
    rng = np.random.default_rng(42)
    fs = 250
    X = rng.normal(size=(2, 1000))
    
    plv = VireonPLV().compute(X, fs=fs, band=(8, 12))
    assert plv[0, 1] < 0.2
    
def test_pli():
    fs = 250
    t = np.arange(0, 4, 1/fs)
    x1 = np.sin(2 * np.pi * 10 * t)
    # phase shift pi/2 -> sin to cos
    x2 = np.cos(2 * np.pi * 10 * t)
    X = np.vstack([x1, x2])
    
    pli = VireonPLI().compute(X, fs=fs, band=(8, 12))
    # PLI should be approx 1 since phase diff is constant pi/2 (imag part is 1, sign is 1)
    assert pli[0, 1] > 0.95
    
def test_aec():
    np.random.default_rng(42)
    fs = 250
    t = np.arange(0, 4, 1/fs)
    # same envelope, different carriers
    env = np.sin(2 * np.pi * 2 * t) + 2
    x1 = env * np.sin(2 * np.pi * 10 * t)
    x2 = env * np.cos(2 * np.pi * 20 * t)
    X = np.vstack([x1, x2])
    
    aec = VireonAEC().compute(X, fs=fs, band=(1, 30))
    # AEC might not be perfect 1.0 due to bandpass filter changing things, but should be high
    assert aec[0, 1] > 0.5
    
def test_symmetric():
    rng = np.random.default_rng(42)
    X = rng.normal(size=(3, 1000))
    fs = 250
    band = (8, 12)
    
    coh = VireonCoherence().compute(X, fs)
    assert np.allclose(coh, coh.T)
    
    plv = VireonPLV().compute(X, fs, band)
    assert np.allclose(plv, plv.T)
    
    pli = VireonPLI().compute(X, fs, band)
    assert np.allclose(pli, pli.T)
    
    aec = VireonAEC().compute(X, fs, band)
    assert np.allclose(aec, aec.T)
    
def test_rejects_nan():
    X = np.ones((2, 100))
    X[0, 0] = np.nan
    fs = 250
    
    with pytest.raises(ScientificContractViolation):
        VireonCoherence().compute(X, fs)
    with pytest.raises(ScientificContractViolation):
        VireonPLV().compute(X, fs, (8, 12))

def test_wpli_locked():
    fs = 250
    t = np.arange(0, 4, 1/fs)
    # Phase shift of pi/4 means imaginary part is non-zero and consistently of one sign
    x1 = np.sin(2 * np.pi * 10 * t)
    x2 = np.sin(2 * np.pi * 10 * t + np.pi/4)
    X = np.vstack([x1, x2])
    
    wpli = VireonWPLI().compute(X, fs=fs, band=(8, 12))
    assert wpli[0, 1] > 0.8
    assert 0 <= wpli[0, 1] <= 1.0

def test_wpli_noise():
    rng = np.random.default_rng(42)
    fs = 250
    X = rng.normal(size=(2, 10000))
    
    wpli = VireonWPLI().compute(X, fs=fs, band=(8, 12))
    assert wpli[0, 1] < 0.2
    assert 0 <= wpli[0, 1] <= 1.0
