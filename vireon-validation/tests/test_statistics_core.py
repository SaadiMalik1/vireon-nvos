import numpy as np
import pytest
from vireon_validation.statistics import compute_bootstrap_ci

def test_compute_bootstrap_ci():
    from vireon_core.runtime.rng import DeterministicRNG
    rng = DeterministicRNG(seed=42)
    # Generate random normal data (mean = 0, std = 1)
    data = rng.normal(loc=0.0, scale=1.0, size=100)
    
    def mean_statistic(sample):
        return np.mean(sample)
    
    point_est, var, ci = compute_bootstrap_ci(data, mean_statistic, n_resamples=500)
    
    # Point estimate should be close to 0
    assert abs(point_est) < 0.2
    
    # CI should surround the point estimate
    assert ci[0] < point_est < ci[1]
    
    # Variance should be > 0
    assert var > 0.0
    
def test_compute_bootstrap_ci_small_data():
    data = np.array([1.0, 2.0, 3.0])
    
    def sum_stat(sample):
        return np.sum(sample)
        
    point_est, var, ci = compute_bootstrap_ci(data, sum_stat)
    
    assert point_est == 6.0
    assert var == 0.0
    assert ci == [6.0, 6.0]
