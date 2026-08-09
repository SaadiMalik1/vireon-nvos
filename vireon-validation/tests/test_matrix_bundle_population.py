import numpy as np
from vireon_core.contracts.evidence import EvidenceBundle
from vireon_core.runtime.rng import DeterministicRNG
from vireon_validation.benchmarks.matrix import BenchmarkMatrix
from vireon_methods.machine_learning.csp import CSPPlugin

class DatasetWrapper:
    def __init__(self, data, labels=None, doi="10.1000/182"):
        self.data = data
        self.labels = labels
        self.doi = doi

def _make_test_dataset(seed=42):
    """Create a deterministic test dataset with real ERD pattern."""
    rng = DeterministicRNG(seed=seed)
    n_epochs, n_channels, n_samples = 20, 8, 250
    X = np.zeros((n_epochs, n_channels, n_samples))
    y = np.array([0, 1] * (n_epochs // 2))
    for i in range(n_epochs):
        if y[i] == 0:
            # Class 0: high mu-band power
            X[i] = rng.normal(0, 1, (n_channels, n_samples)) + 5 * np.sin(
                2 * np.pi * 10 * np.arange(n_samples) / 250
            )[None, :]
        else:
            # Class 1: low mu-band power (ERD)
            X[i] = rng.normal(0, 1, (n_channels, n_samples))
    return DatasetWrapper(data=X, labels=y)

def test_matrix_populates_evidence_hash():
    """Evidence bundle must have non-empty 64-char hex evidence_hash."""
    matrix = BenchmarkMatrix()
    matrix.add_method(CSPPlugin(n_components=2))
    matrix.add_dataset("test", _make_test_dataset())
    bundles = matrix.execute_matrix()
    assert len(bundles) > 0
    for bundle_dict in bundles:
        bundle = EvidenceBundle(**bundle_dict) if isinstance(bundle_dict, dict) else bundle_dict
        assert bundle.evidence_hash != "", "evidence_hash must be non-empty"
        assert len(bundle.evidence_hash) == 64, "evidence_hash must be 64-char hex"

def test_matrix_populates_algorithm_field():
    """Algorithm field must be populated with plugin_id."""
    matrix = BenchmarkMatrix()
    csp = CSPPlugin(n_components=2)
    matrix.add_method(csp)
    matrix.add_dataset("test", _make_test_dataset())
    bundles = matrix.execute_matrix()
    bundle = EvidenceBundle(**bundles[0])
    assert bundle.algorithm == csp.plugin_id

def test_matrix_measures_runtime():
    """runtime_sec must be a real measured value, not 0.0."""
    matrix = BenchmarkMatrix()
    matrix.add_method(CSPPlugin(n_components=2))
    matrix.add_dataset("test", _make_test_dataset())
    bundles = matrix.execute_matrix()
    bundle = EvidenceBundle(**bundles[0])
    assert bundle.runtime_sec > 0.0

def test_conclusion_verdict_equals_pass_fail():
    """conclusion_verdict must always equal pass_fail."""
    matrix = BenchmarkMatrix()
    matrix.add_method(CSPPlugin(n_components=2))
    matrix.add_dataset("test", _make_test_dataset())
    bundles = matrix.execute_matrix()
    bundle = EvidenceBundle(**bundles[0])
    assert bundle.conclusion_verdict == bundle.pass_fail

def test_evidence_hash_deterministic_for_same_input():
    """Same data + seed -> same hash."""
    matrix1 = BenchmarkMatrix(seed=42)
    matrix1.add_method(CSPPlugin(n_components=2))
    matrix1.add_dataset("test", _make_test_dataset(seed=42))
    b1 = matrix1.execute_matrix()
    
    matrix2 = BenchmarkMatrix(seed=42)
    matrix2.add_method(CSPPlugin(n_components=2))
    matrix2.add_dataset("test", _make_test_dataset(seed=42))
    b2 = matrix2.execute_matrix()
    
    bundle1 = EvidenceBundle(**b1[0])
    bundle2 = EvidenceBundle(**b2[0])
    assert bundle1.evidence_hash == bundle2.evidence_hash

def test_evidence_hash_differs_for_different_input():
    """Different data -> different hash."""
    matrix1 = BenchmarkMatrix(seed=42)
    matrix1.add_method(CSPPlugin(n_components=2))
    matrix1.add_dataset("test", _make_test_dataset(seed=42))
    b1 = matrix1.execute_matrix()
    
    matrix2 = BenchmarkMatrix(seed=42)
    matrix2.add_method(CSPPlugin(n_components=2))
    matrix2.add_dataset("test", _make_test_dataset(seed=999))
    b2 = matrix2.execute_matrix()
    
    bundle1 = EvidenceBundle(**b1[0])
    bundle2 = EvidenceBundle(**b2[0])
    assert bundle1.evidence_hash != bundle2.evidence_hash
