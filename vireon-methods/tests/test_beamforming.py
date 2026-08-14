import numpy as np
import pytest
from vireon_methods.source_localization.vireon_beamforming import VireonLCMV
from vireon_core.contracts.plugin import ScientificContractViolation

def test_lcmv_shape():
    rng = np.random.default_rng(42)
    n_sensors = 10
    n_sources = 5
    n_samples = 100
    
    leadfield = rng.normal(size=(n_sensors, n_sources))
    X = rng.normal(size=(n_sensors, n_samples))
    
    lcmv = VireonLCMV(leadfield)
    lcmv.fit(X)
    source_est = lcmv.apply(X)
    
    assert source_est.shape == (n_sources, n_samples)
    
def test_lcmv_localizes_known_source():
    rng = np.random.default_rng(42)
    n_sensors = 10
    n_sources = 5
    n_samples = 500
    
    leadfield = rng.normal(size=(n_sensors, n_sources))
    
    true_source = np.zeros((n_sources, n_samples))
    true_source[2, :] = np.sin(np.linspace(0, 10 * np.pi, n_samples))
    
    X = leadfield @ true_source + 0.1 * rng.normal(size=(n_sensors, n_samples))
    
    lcmv = VireonLCMV(leadfield, reg=0.01)
    lcmv.fit(X)
    source_est = lcmv.apply(X)
    
    var_est = np.var(source_est, axis=1)
    assert np.argmax(var_est) == 2

def test_lcmv_rejects_nan():
    leadfield = np.ones((10, 5))
    X = np.ones((10, 100))
    X[0, 0] = np.nan
    
    lcmv = VireonLCMV(leadfield)
    with pytest.raises(ScientificContractViolation):
        lcmv.fit(X)
        
    lcmv.fit(np.ones((10, 100)))
    with pytest.raises(ScientificContractViolation):
        lcmv.apply(X)
        
def test_lcmv_not_fitted():
    leadfield = np.ones((10, 5))
    X = np.ones((10, 100))
    lcmv = VireonLCMV(leadfield)
    with pytest.raises(ValueError, match="not fitted"):
        lcmv.apply(X)
