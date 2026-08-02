import pytest
import numpy as np
from vireon_core.contracts.evidence import EvidenceBundle
from vireon_core.runtime.rng import DeterministicRNG
from vireon_validation.benchmarks.matrix import BenchmarkMatrix
from vireon_methods.machine_learning.csp import CSPPlugin

def test_add_dataset_accepts_data_and_labels():
    matrix = BenchmarkMatrix()
    rng = DeterministicRNG(seed=0)
    X = rng.normal(0, 1, size=(20, 8, 250))
    y = np.array([0, 1] * 10)
    matrix.add_dataset("test", data=X, labels=y)
    assert "test" in matrix.datasets
    assert matrix.datasets["test"]["data"] is X
    assert matrix.datasets["test"]["labels"] is y

def test_add_dataset_without_data_marks_as_none():
    matrix = BenchmarkMatrix()
    matrix.add_dataset("empty")
    assert matrix.datasets["empty"] is None

def test_synthetic_motor_imagery_has_erd_pattern():
    """CSP must achieve >0.7 accuracy on synthetic data (proving ERD exists)."""
    import sys
    import os
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    demo_dir = os.path.join(repo_root, "examples", "first_validation")
    if demo_dir not in sys.path:
        sys.path.insert(0, demo_dir)
    from demo import _generate_synthetic_motor_imagery
    
    X, y = _generate_synthetic_motor_imagery(seed=42)
    from mne.decoding import CSP
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
    from sklearn.model_selection import cross_val_score
    from sklearn.pipeline import make_pipeline
    
    csp = CSP(n_components=4, reg=None, log=True)
    lda = LinearDiscriminantAnalysis()
    clf = make_pipeline(csp, lda)
    scores = cross_val_score(clf, X, y, cv=5)
    assert scores.mean() > 0.7, f"CSP accuracy {scores.mean():.2f} < 0.7 — no ERD pattern"

def test_matrix_receives_real_data():
    """execute_matrix must call method.execute with non-None signal."""
    import sys
    import os
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    demo_dir = os.path.join(repo_root, "examples", "first_validation")
    if demo_dir not in sys.path:
        sys.path.insert(0, demo_dir)
    from demo import _generate_synthetic_motor_imagery

    matrix = BenchmarkMatrix(seed=42)
    matrix.add_method(CSPPlugin(n_components=2))
    X, y = _generate_synthetic_motor_imagery(seed=42)
    matrix.add_dataset("test", data=X, labels=y)
    bundles = matrix.execute_matrix()
    assert len(bundles) > 0
    assert any(b["success"] is True for b in bundles)
