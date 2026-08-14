import numpy as np
import pytest
from vireon_methods.source_localization.vireon_source_localization import VireonMinimumNorm
from vireon_core.contracts.plugin import ScientificContractViolation

def test_mne_shape():
    rng = np.random.default_rng(42)
    n_sensors = 10
    n_sources = 5
    n_samples = 100
    
    leadfield = rng.normal(size=(n_sensors, n_sources))
    X = rng.normal(size=(n_sensors, n_samples))
    
    mne = VireonMinimumNorm(leadfield)
    source_est = mne.fit(X)
    
    assert source_est.shape == (n_sources, n_samples)
    
def test_mne_localizes_known_source():
    rng = np.random.default_rng(42)
    n_sensors = 10
    n_sources = 5
    n_samples = 500
    
    leadfield = rng.normal(size=(n_sensors, n_sources))
    
    true_source = np.zeros((n_sources, n_samples))
    true_source[2, :] = np.sin(np.linspace(0, 10 * np.pi, n_samples))
    
    X = leadfield @ true_source + 0.01 * rng.normal(size=(n_sensors, n_samples))
    
    mne = VireonMinimumNorm(leadfield, snr=10.0)
    source_est = mne.fit(X)
    
    var_est = np.var(source_est, axis=1)
    assert np.argmax(var_est) == 2

def test_mne_lambda2_used():
    rng = np.random.default_rng(42)
    leadfield = rng.normal(size=(10, 5))
    X = rng.normal(size=(10, 100))
    
    mne1 = VireonMinimumNorm(leadfield, snr=3.0)
    source_est1 = mne1.fit(X)
    
    mne2 = VireonMinimumNorm(leadfield, snr=0.1)
    source_est2 = mne2.fit(X)
    
    assert not np.allclose(source_est1, source_est2)

def test_mne_rejects_nan():
    leadfield = np.ones((10, 5))
    X = np.ones((10, 100))
    X[0, 0] = np.nan
    
    mne = VireonMinimumNorm(leadfield)
    with pytest.raises(ScientificContractViolation):
        mne.fit(X)
