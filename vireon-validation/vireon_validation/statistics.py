import numpy as np
from scipy import stats
from typing import Callable, Tuple, Any

def compute_bootstrap_ci(data: np.ndarray, statistic_fn: Callable, n_resamples: int = 1000) -> Tuple[float, float, list[float]]:
    """
    Computes the point estimate, variance, and 95% bootstrap confidence interval
    for a given statistic function.

    Args:
        data: 1D or 2D array of samples
        statistic_fn: Function that takes data and returns a scalar
        n_resamples: Number of bootstrap iterations

    Returns:
        (point_estimate, variance, [ci_lower, ci_upper])
    """
    point_estimate = float(statistic_fn(data))
    
    # Check if data is too small to resample meaningfully
    if len(data) < 5:
        return point_estimate, 0.0, [point_estimate, point_estimate]

    # Use scipy's bootstrap (requires 1D array of samples along axis=0)
    # The statistic function must accept `axis` argument for scipy.stats.bootstrap
    # Since our custom functions don't, we can write a quick manual bootstrap or adapt it.
    
    # Manual 1D bootstrap for simplicity and compatibility with custom metric functions
    n = len(data)
    bootstrap_samples = []
    
    # Use deterministic seeded RNG for bootstrap CI
    rng = np.random.default_rng(42)
    
    for _ in range(n_resamples):
        indices = rng.integers(0, n, size=n)
        sample = data[indices]
        val = statistic_fn(sample)
        bootstrap_samples.append(val)
        
    bootstrap_samples = np.array(bootstrap_samples)
    variance = float(np.var(bootstrap_samples))
    ci_lower = float(np.percentile(bootstrap_samples, 2.5))
    ci_upper = float(np.percentile(bootstrap_samples, 97.5))
    
    return point_estimate, variance, [ci_lower, ci_upper]

def compute_cohens_d(x: np.ndarray, y: np.ndarray) -> float:
    """
    Computes Cohen's d effect size between two independent samples.
    """
    nx, ny = len(x), len(y)
    if nx < 2 or ny < 2:
        return 0.0
    
    dof = nx + ny - 2
    pool_var = ((nx - 1) * np.var(x, ddof=1) + (ny - 1) * np.var(y, ddof=1)) / dof
    if pool_var == 0:
        return 0.0
        
    d = (np.mean(x) - np.mean(y)) / np.sqrt(pool_var)
    return float(d)

def compute_permutation_test(x: np.ndarray, y: np.ndarray, n_permutations: int = 1000) -> float:
    """
    Computes the p-value for the difference in means between two groups using a permutation test.
    """
    nx, ny = len(x), len(y)
    if nx < 2 or ny < 2:
        return 1.0
        
    observed_diff = np.abs(np.mean(x) - np.mean(y))
    pooled_data = np.concatenate([x, y])
    
    rng = np.random.default_rng(42)
    
    count = 0
    for _ in range(n_permutations):
        rng.shuffle(pooled_data)
        perm_x = pooled_data[:nx]
        perm_y = pooled_data[nx:]
        perm_diff = np.abs(np.mean(perm_x) - np.mean(perm_y))
        if perm_diff >= observed_diff:
            count += 1
            
    return float(count / n_permutations)
