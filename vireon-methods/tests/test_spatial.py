import numpy as np
import pytest
from vireon_methods.native.spatial import VireonLaplacian, VireonREST
from vireon_core.contracts.plugin import ScientificContractViolation

def test_laplacian_no_defaults():
    with pytest.raises(TypeError):
        VireonLaplacian()

def test_laplacian_output():
    rng = np.random.default_rng(42)
    data = rng.normal(size=(3, 10))
    pos = np.array([[0, 0, 1], [0, 1, 0], [1, 0, 0]])
    
    lap = VireonLaplacian(pos, n_neighbors=2)
    out = lap.apply(data)
    
    assert out.shape == (3, 10)
    assert not np.allclose(out, data * 0.95)
    
    expected_ch0 = data[0] - np.mean(data[[1, 2]], axis=0)
    assert np.allclose(out[0], expected_ch0)
    
def test_laplacian_rejects_nan():
    pos = np.array([[0, 0, 1], [0, 1, 0]])
    lap = VireonLaplacian(pos, n_neighbors=1)
    data = np.ones((2, 10))
    data[0, 0] = np.nan
    with pytest.raises(ScientificContractViolation):
        lap.apply(data)
        
def test_rest_no_defaults():
    with pytest.raises(TypeError):
        VireonREST()

def test_rest_output():
    rng = np.random.default_rng(42)
    data = rng.normal(size=(3, 10))
    leadfield = rng.normal(size=(3, 5))
    
    rest = VireonREST(leadfield)
    out = rest.apply(data)
    
    assert out.shape == (3, 10)
    assert not np.allclose(out, data * 0.99)
    
def test_rest_rejects_nan():
    leadfield = np.ones((3, 5))
    rest = VireonREST(leadfield)
    data = np.ones((3, 10))
    data[0, 0] = np.nan
    with pytest.raises(ScientificContractViolation):
        rest.apply(data)
