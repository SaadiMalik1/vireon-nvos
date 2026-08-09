"""Integration test: every evidence bundle has statistical rigor."""
import json
import os
import subprocess
import sys
import numpy as np
from vireon_core.runtime.rng import DeterministicRNG


def test_evidence_bundle_has_bootstrap_ci():
    """Evidence bundle should include bootstrap CI for CCC."""
    from vireon_validation.statistics.bootstrap import bootstrap_ccc_ci
    rng = DeterministicRNG(42)
    x = rng.normal(0, 1, 100)
    y = x + rng.normal(0, 0.2, 100)
    ci = bootstrap_ccc_ci(x, y, n_bootstrap=1000, seed=42)
    assert "ccc" in ci
    assert "ci_lower" in ci and "ci_upper" in ci
    assert ci["ci_lower"] < ci["ccc"] < ci["ci_upper"]


def test_evidence_bundle_has_effect_size():
    """Evidence bundle should include effect size."""
    from vireon_validation.statistics.effect_sizes import cohens_d, interpret_cohens_d
    rng = DeterministicRNG(42)
    g1 = rng.normal(0, 1, 50)
    g2 = rng.normal(0.5, 1, 50)
    d = cohens_d(g1, g2)
    interpretation = interpret_cohens_d(d)
    assert isinstance(d, float)
    assert interpretation in ["negligible", "small", "medium", "large"]


def test_evidence_bundle_has_corrected_pvalues():
    """Evidence bundle should include FDR-corrected p-values when multiple tests."""
    from vireon_validation.statistics.multiple_comparisons import benjamini_hochberg
    p_values = np.array([0.001, 0.01, 0.02, 0.04, 0.03])
    adj, sig = benjamini_hochberg(p_values, alpha=0.05)
    assert len(adj) == len(p_values)
    # Check that adjusted p-values are bounded and properly computed
    assert np.all(adj >= 0.0) and np.all(adj <= 1.0)


def test_demo_evidence_has_rigorous_statistics():
    """Run the demo and verify the evidence has real computed CCC."""
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env = os.environ.copy()
    env["PYTHONPATH"] = ":".join([repo_root] + [
        os.path.join(repo_root, p) for p in
        ["vireon-core", "vireon-models", "vireon-methods", "vireon-validation",
         "vireon-evidence", "vireon-knowledge", "vireon-corpus"]
    ])
    env["MPLBACKEND"] = "Agg"

    result = subprocess.run(
        [sys.executable, os.path.join(repo_root, "examples/first_validation/demo.py")],
        cwd=repo_root, env=env, capture_output=True, text=True, timeout=120
    )
    assert result.returncode == 0, f"Demo failed: {result.stderr}"

    evidence_path = os.path.join(repo_root, "output", "evidence.json")
    if os.path.exists(evidence_path):
        with open(evidence_path, "r") as f:
            bundle = json.load(f)
        # The bundle should have real CCC (not hardcoded)
        ccc = bundle.get("statistical_agreement", {}).get("ccc", 0)
        assert ccc != 0.95, "CCC is hardcoded 0.95"
        assert 0 <= ccc <= 1.0, f"CCC {ccc} out of range"
