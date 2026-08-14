import numpy as np
import pytest
import scipy.linalg
from sklearn.decomposition import FastICA
from vireon_methods.spatial.vireon_ica import VireonICA
from vireon_core.contracts.plugin import ScientificContractViolation

def test_ica_matches_sklearn_subspace():
    rng = np.random.default_rng(42)
    S = rng.laplace(size=(1000, 3))  # non-Gaussian sources
    A = rng.normal(size=(3, 3))  # mixing
    X = S @ A.T
    
    ica_v = VireonICA(n_components=3, max_iter=200, tol=1e-4).fit(X)
    ica_s = FastICA(n_components=3, random_state=42, max_iter=200, tol=1e-4, fun='logcosh', whiten='unit-variance').fit(X)
    
    sub_v = ica_v.components_  
    sub_s = ica_s.components_
    
    O_v = scipy.linalg.orth(sub_v.T)
    O_s = scipy.linalg.orth(sub_s.T)
    
    _, singular_values, _ = np.linalg.svd(O_v.T @ O_s)
    
    assert np.allclose(singular_values, 1.0, atol=1e-4), "Subspaces must match"

def test_ica_returns_mixing_matrix():
    X = np.random.default_rng(0).normal(size=(1000, 4))
    ica = VireonICA(n_components=2).fit(X)
    assert ica.mixing_.shape == (4, 2)
    
def test_ica_rejects_too_many_components():
    X = np.random.default_rng(0).normal(size=(100, 3))
    with pytest.raises((ValueError, ScientificContractViolation)):
        VireonICA(n_components=5).fit(X)

def test_ica_rejects_nan():
    X = np.array([[1.0, np.nan], [2.0, 3.0]])
    with pytest.raises(ScientificContractViolation):
        VireonICA(n_components=1).fit(X)
