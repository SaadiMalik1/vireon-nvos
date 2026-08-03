import numpy as np
import pytest
from vireon_core.runtime.rng import DeterministicRNG
from vireon_validation.statistics.bootstrap import (
    bootstrap_ci,
    bootstrap_ccc_ci,
    bootstrap_accuracy_ci,
    bootstrap_rmse_ci,
)


def test_bootstrap_ci_basic():
    rng = DeterministicRNG(42)
    data = rng.normal(10, 2, 1000)
    point, lo, hi = bootstrap_ci(data, np.mean, n_bootstrap=1000, seed=42)
    assert abs(point - 10) < 0.2
    assert lo < point < hi
    assert (hi - lo) < 1.0  # CI should be narrow for n=1000


def test_bootstrap_ci_coverage():
    """95% CI should contain the true mean ~95% of the time."""
    rng = DeterministicRNG(42)
    true_mean = 5.0
    contains_count = 0
    n_trials = 100
    for i in range(n_trials):
        data = rng.normal(true_mean, 1, 100)
        _, lo, hi = bootstrap_ci(data, np.mean, n_bootstrap=500, seed=i)
        if lo <= true_mean <= hi:
            contains_count += 1
    # Should be ~95 out of 100
    assert contains_count > 85, f"CI coverage {contains_count}/{n_trials} < 85%"


def test_bootstrap_ccc_ci():
    rng = DeterministicRNG(42)
    x = rng.normal(0, 1, 500)
    y = x + rng.normal(0, 0.1, 500)  # high concordance
    result = bootstrap_ccc_ci(x, y, n_bootstrap=1000, seed=42)
    assert result["ccc"] > 0.95
    assert result["ci_lower"] < result["ccc"] < result["ci_upper"]


def test_bootstrap_accuracy_ci():
    y_true = np.array([0, 1] * 50)
    y_pred = np.array([0, 1] * 45 + [1, 0] * 5)  # 90% accuracy
    result = bootstrap_accuracy_ci(y_true, y_pred, n_bootstrap=1000, seed=42)
    assert result["accuracy"] == 0.9
    assert result["ci_lower"] < 0.9 < result["ci_upper"]


def test_bootstrap_rmse_ci():
    rng = DeterministicRNG(42)
    x = rng.normal(0, 1, 500)
    y = x + rng.normal(0, 0.5, 500)
    result = bootstrap_rmse_ci(x, y, n_bootstrap=1000, seed=42)
    assert 0.4 < result["rmse"] < 0.6
    assert result["ci_lower"] < result["rmse"] < result["ci_upper"]


def test_bootstrap_deterministic():
    """Same seed -> same CI."""
    rng = DeterministicRNG(42)
    data = rng.normal(0, 1, 100)
    r1 = bootstrap_ci(data, np.mean, n_bootstrap=500, seed=42)
    r2 = bootstrap_ci(data, np.mean, n_bootstrap=500, seed=42)
    assert r1 == r2
