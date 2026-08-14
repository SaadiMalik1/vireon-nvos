import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
from vireon_validation.statistics.permutation import (
    permutation_test,
    max_stat_permutation_test,
    cluster_based_permutation_test,
)


def test_permutation_test_significant():
    rng = DeterministicRNG(42)
    g1 = rng.normal(5, 1, 50)
    g2 = rng.normal(6, 1, 50)  # different mean
    result = permutation_test(g1, g2, n_permutations=1000, seed=42)
    assert result["p_value"] < 0.05, f"p={result['p_value']} should be < 0.05"


def test_permutation_test_not_significant():
    rng = DeterministicRNG(42)
    g1 = rng.normal(5, 1, 50)
    g2 = rng.normal(5, 1, 50)  # same mean
    result = permutation_test(g1, g2, n_permutations=1000, seed=42)
    assert result["p_value"] > 0.05, f"p={result['p_value']} should be > 0.05"


def test_max_stat_corrects_for_multiple_comparisons():
    """Max-stat test should be more conservative than uncorrected."""
    rng = DeterministicRNG(42)
    n_obs, n_comp = 20, 100
    data = rng.normal(0, 1, (n_obs, n_comp))
    labels = np.array([0] * 10 + [1] * 10)
    result = max_stat_permutation_test(data, labels, n_permutations=200, seed=42)
    # With no real effect, false positive rate should be well controlled
    assert np.mean(result["p_values"] < 0.05) < 0.1


def test_cluster_based_permutation_test():
    """Test cluster-based permutation test on 3D time-frequency data."""
    rng = DeterministicRNG(42)
    n_sub = 15
    n_time = 10
    n_freq = 8

    # Condition 1: pure noise
    d1 = rng.normal(0, 1, (n_sub, n_time, n_freq))
    # Condition 2: noise + strong localized cluster at t=[3..5], f=[2..4]
    d2 = rng.normal(0, 1, (n_sub, n_time, n_freq))
    d2[:, 3:6, 2:5] += 2.5

    result = cluster_based_permutation_test(d1, d2, threshold=0.05, n_permutations=200, seed=42)
    assert result["n_clusters"] >= 1
    assert len(result["cluster_masses"]) >= 1
    # The true effect cluster should have a significant p-value
    assert min(result["p_values"]) < 0.05
