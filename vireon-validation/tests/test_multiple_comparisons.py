import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
from vireon_validation.statistics.multiple_comparisons import (
    bonferroni_correction,
    benjamini_hochberg,
    holm_bonferroni,
)


def test_bonferroni_basic():
    p = np.array([0.01, 0.02, 0.03, 0.04, 0.05])
    adj, sig = bonferroni_correction(p, alpha=0.05)
    assert np.allclose(adj, np.minimum(p * 5, 1.0))
    assert not sig.any()  # none strictly < 0.05 (0.01*5 = 0.05)


def test_bh_fdr_control():
    """BH should control FDR and detect false nulls."""
    rng = DeterministicRNG(42)
    n_tests = 100
    n_true_null = 90  # 90% are true null
    n_false_null = n_tests - n_true_null

    p_values = np.zeros(n_tests)
    p_values[:n_true_null] = rng.uniform(0, 1, n_true_null)
    p_values[n_true_null:] = rng.beta(0.1, 50, n_false_null)  # strong signal -> small p-values

    adj, sig = benjamini_hochberg(p_values, alpha=0.05)
    detected_false = np.sum(sig[n_true_null:])
    assert detected_false > n_false_null * 0.5, f"Only detected {detected_false}/{n_false_null} false nulls"


def test_bh_more_powerful_than_bonferroni():
    """BH should declare at least as many significant tests as Bonferroni."""
    p = np.array([0.001, 0.005, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08])
    _, sig_bonf = bonferroni_correction(p, alpha=0.05)
    _, sig_bh = benjamini_hochberg(p, alpha=0.05)
    assert np.sum(sig_bh) >= np.sum(sig_bonf)


def test_holm_step_down():
    """Holm-Bonferroni should be step-down (monotonic adjusted p-values)."""
    p = np.array([0.01, 0.04, 0.03, 0.001])
    adj, sig = holm_bonferroni(p, alpha=0.05)
    # Smallest raw p-value should have smallest adjusted p
    assert adj[3] <= adj[0]  # p=0.001 < p=0.01
