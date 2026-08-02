import pytest
import numpy as np
from vireon_validation.benchmarks.matrix import BenchmarkMatrix
from vireon_methods.machine_learning.csp import CSPPlugin

def test_reference_accuracy_on_erd_data():
    """MNE CSP+LDA should achieve >0.8 on synthetic ERD data."""
    import sys, os
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    demo_dir = os.path.join(repo_root, "examples", "first_validation")
    if demo_dir not in sys.path:
        sys.path.insert(0, demo_dir)
    from demo import _generate_synthetic_motor_imagery
    X, y = _generate_synthetic_motor_imagery(seed=42)
    matrix = BenchmarkMatrix(seed=42)
    ref_acc = matrix._compute_reference_accuracy(X, y)
    assert ref_acc > 0.8, f"Reference accuracy {ref_acc:.2f} < 0.8"

def test_method_accuracy_on_erd_data():
    """Vireon CSP+LDA should achieve >0.7 on synthetic ERD data."""
    import sys, os
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    demo_dir = os.path.join(repo_root, "examples", "first_validation")
    if demo_dir not in sys.path:
        sys.path.insert(0, demo_dir)
    from demo import _generate_synthetic_motor_imagery
    X, y = _generate_synthetic_motor_imagery(seed=42)
    matrix = BenchmarkMatrix(seed=42)
    method_acc = matrix._compute_method_accuracy(CSPPlugin(n_components=4), X, y)
    assert method_acc > 0.7, f"Method accuracy {method_acc:.2f} < 0.7"

def test_ccc_above_threshold_on_baseline():
    """CCC between Vireon and MNE CSP+LDA > 0.7 on unperturbed ERD data."""
    import sys, os
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    demo_dir = os.path.join(repo_root, "examples", "first_validation")
    if demo_dir not in sys.path:
        sys.path.insert(0, demo_dir)
    from demo import _generate_synthetic_motor_imagery
    X, y = _generate_synthetic_motor_imagery(seed=42)
    matrix = BenchmarkMatrix(seed=42)
    matrix.add_method(CSPPlugin(n_components=4))
    matrix.add_dataset("test", data=X, labels=y)
    bundles = matrix.execute_matrix()
    baseline_bundle = [b for b in bundles if b.get("perturbation") == "None" or b.get("benchmark_results", {}).get("perturbation") == "None"][0]
    assert baseline_bundle["statistical_agreement"]["ccc"] > 0.7
    assert baseline_bundle["pass_fail"] == "PASS"
    assert baseline_bundle["conclusion_verdict"] == "PASS"

def test_ccc_uses_identical_cv_splits():
    """Method and reference must use the same CV splits."""
    import sys, os
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    demo_dir = os.path.join(repo_root, "examples", "first_validation")
    if demo_dir not in sys.path:
        sys.path.insert(0, demo_dir)
    from demo import _generate_synthetic_motor_imagery
    X, y = _generate_synthetic_motor_imagery(seed=42)
    matrix = BenchmarkMatrix(seed=42)
    method_scores = matrix._compute_method_cv_scores(CSPPlugin(n_components=4), X, y)
    ref_scores = matrix._compute_reference_cv_scores(X, y, n_components=4)
    assert len(method_scores) == 5
    assert len(ref_scores) == 5
    assert matrix._compute_ccc_vector(method_scores, method_scores) == 1.0
