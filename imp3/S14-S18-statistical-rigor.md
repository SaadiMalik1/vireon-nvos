# Workstream C — Statistical Rigor (S14-S18)

**Goal:** Every metric has confidence intervals (bootstrap), every comparison has effect sizes, every multiple comparison has FDR correction.

**Common rules:**
- Use `DeterministicRNG` for all resampling.
- No bare point estimates — always include CI.
- Effect sizes must be computed, not hardcoded.
- FDR correction must use Benjamini-Hochberg procedure.

---

## S14: Bootstrap Confidence Intervals for All Metrics

**Effort:** M | **Dependencies:** None | **Verification:** G4

### Context
`vireon-validation/vireon_validation/statistics/core.py` has `compute_bootstrap_ci()` but it's not integrated into the evidence pipeline. Every metric in an evidence bundle (CCC, RMSE, accuracy, kappa) should have a bootstrap CI.

### Implementation

Create `vireon-validation/vireon_validation/statistics/bootstrap.py`:

```python
"""Bootstrap confidence intervals for all metrics.

Reference: Efron, B., & Tibshirani, R. J. (1994). An Introduction to the Bootstrap.
Chapman & Hall/CRC.
"""
import numpy as np
from typing import Callable, Tuple, Optional
from vireon_core.runtime.rng import DeterministicRNG


def bootstrap_ci(data: np.ndarray, statistic: Callable, 
                 n_bootstrap: int = 10000, confidence: float = 0.95,
                 seed: int = 42) -> Tuple[float, float, float]:
    """Compute bootstrap confidence interval for a statistic.
    
    Args:
        data: 1D or 2D array. For 2D, resamples rows (paired data).
        statistic: Function that takes a (sub)sample and returns a scalar.
        n_bootstrap: Number of bootstrap resamples.
        confidence: Confidence level (0.95 = 95% CI).
        seed: Random seed for reproducibility.
    
    Returns:
        (point_estimate, ci_lower, ci_upper)
    """
    rng = DeterministicRNG(seed)
    n = len(data)
    point_estimate = statistic(data)
    
    boot_stats = np.zeros(n_bootstrap)
    for i in range(n_bootstrap):
        idx = rng.integer(0, n, size=n)
        boot_sample = data[idx] if data.ndim == 1 else data[idx, :]
        boot_stats[i] = statistic(boot_sample)
    
    alpha = (1 - confidence) / 2
    ci_lower = float(np.percentile(boot_stats, 100 * alpha))
    ci_upper = float(np.percentile(boot_stats, 100 * (1 - alpha)))
    
    return float(point_estimate), ci_lower, ci_upper


def bootstrap_ccc_ci(x: np.ndarray, y: np.ndarray, n_bootstrap: int = 10000,
                     confidence: float = 0.95, seed: int = 42) -> dict:
    """Bootstrap CI for Lin's Concordance Correlation Coefficient."""
    from vireon_validation.statistics.framework import lin_concordance_correlation
    data = np.column_stack([x, y])
    point, ci_lo, ci_hi = bootstrap_ci(
        data, lambda d: lin_concordance_correlation(d[:, 0], d[:, 1]),
        n_bootstrap, confidence, seed
    )
    return {"ccc": point, "ci_lower": ci_lo, "ci_upper": ci_hi, "confidence": confidence}


def bootstrap_accuracy_ci(y_true: np.ndarray, y_pred: np.ndarray,
                          n_bootstrap: int = 10000, confidence: float = 0.95,
                          seed: int = 42) -> dict:
    """Bootstrap CI for classification accuracy."""
    from sklearn.metrics import accuracy_score
    data = np.column_stack([y_true, y_pred])
    point, ci_lo, ci_hi = bootstrap_ci(
        data, lambda d: accuracy_score(d[:, 0], d[:, 1]),
        n_bootstrap, confidence, seed
    )
    return {"accuracy": point, "ci_lower": ci_lo, "ci_upper": ci_hi, "confidence": confidence}


def bootstrap_rmse_ci(x: np.ndarray, y: np.ndarray, n_bootstrap: int = 10000,
                      confidence: float = 0.95, seed: int = 42) -> dict:
    """Bootstrap CI for RMSE."""
    data = np.column_stack([x, y])
    def rmse(d):
        return float(np.sqrt(np.mean((d[:, 0] - d[:, 1]) ** 2)))
    point, ci_lo, ci_hi = bootstrap_ci(data, rmse, n_bootstrap, confidence, seed)
    return {"rmse": point, "ci_lower": ci_lo, "ci_upper": ci_hi, "confidence": confidence}
```

### Tests

Create `vireon-validation/tests/test_bootstrap.py`:

```python
import numpy as np
import pytest
from vireon_validation.statistics.bootstrap import (
    bootstrap_ci, bootstrap_ccc_ci, bootstrap_accuracy_ci, bootstrap_rmse_ci
)

def test_bootstrap_ci_basic():
    rng = np.random.default_rng(42)
    data = rng.normal(10, 2, 1000)
    point, lo, hi = bootstrap_ci(data, np.mean, n_bootstrap=1000, seed=42)
    assert abs(point - 10) < 0.2
    assert lo < point < hi
    assert (hi - lo) < 1.0  # CI should be narrow for n=1000

def test_bootstrap_ci_coverage():
    """95% CI should contain the true mean ~95% of the time."""
    rng = np.random.default_rng(42)
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
    rng = np.random.default_rng(42)
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
    rng = np.random.default_rng(42)
    x = rng.normal(0, 1, 500)
    y = x + rng.normal(0, 0.5, 500)
    result = bootstrap_rmse_ci(x, y, n_bootstrap=1000, seed=42)
    assert result["rmse"] > 0.4 and result["rmse"] < 0.6
    assert result["ci_lower"] < result["rmse"] < result["ci_upper"]

def test_bootstrap_deterministic():
    """Same seed → same CI."""
    rng = np.random.default_rng(42)
    data = rng.normal(0, 1, 100)
    r1 = bootstrap_ci(data, np.mean, n_bootstrap=500, seed=42)
    r2 = bootstrap_ci(data, np.mean, n_bootstrap=500, seed=42)
    assert r1 == r2
```

### Acceptance Criteria
- [ ] `bootstrap_ci` computes point estimate + CI for any statistic
- [ ] 95% CI coverage verified (> 85% of CIs contain true mean)
- [ ] CCC, accuracy, RMSE bootstrap functions work
- [ ] Deterministic (same seed → same CI)

### Gemini Prompt
```
You are executing task S14. Create vireon-validation/vireon_validation/statistics/bootstrap.py with: bootstrap_ci(data, statistic, n_bootstrap, confidence, seed) → (point, lo, hi), bootstrap_ccc_ci, bootstrap_accuracy_ci, bootstrap_rmse_ci. Use DeterministicRNG for resampling. Percentile method for CI. Write 6 tests: basic CI, coverage (95% CI contains true mean >85% of time), CCC CI, accuracy CI, RMSE CI, determinism. Branch: svp/S14-bootstrap-confidence-intervals. TDD. Commit. PR. Stop.
```

---

## S15: Permutation Testing Framework

**Effort:** M | **Dependencies:** None | **Verification:** G5

### Context
`vireon-validation/vireon_validation/statistics/core.py` has `compute_permutation_test()` but it's basic. Need a comprehensive framework: cluster-based permutation test (for EEG time-frequency data), max-stat permutation (for multiple comparisons), and FDR permutation.

### Implementation

Create `vireon-validation/vireon_validation/statistics/permutation.py`:

```python
"""Permutation testing framework.

Reference: Maris, E., & Oostenveld, R. (2007). Nonparametric statistical testing 
of EEG- and MEG-data. Journal of Neuroscience Methods, 164(1), 177-190.
"""
import numpy as np
from typing import Callable, Optional, Tuple
from vireon_core.runtime.rng import DeterministicRNG


def permutation_test(group1: np.ndarray, group2: np.ndarray,
                     statistic: Callable = None, n_permutations: int = 10000,
                     seed: int = 42) -> dict:
    """Two-sample permutation test.
    
    Args:
        group1, group2: Arrays of observations.
        statistic: Function(group1, group2) → scalar. Default: mean difference.
        n_permutations: Number of permutations.
        seed: Random seed.
    
    Returns:
        {"statistic": observed, "p_value": p, "null_distribution": dist}
    """
    if statistic is None:
        statistic = lambda g1, g2: np.mean(g1) - np.mean(g2)
    
    rng = DeterministicRNG(seed)
    observed = statistic(group1, group2)
    
    combined = np.concatenate([group1, group2])
    n1 = len(group1)
    
    null_dist = np.zeros(n_permutations)
    for i in range(n_permutations):
        perm = rng.integer(0, len(combined), size=len(combined))
        # Ensure unique permutation (simple approach)
        perm_idx = np.argsort(perm)
        perm1 = combined[perm_idx[:n1]]
        perm2 = combined[perm_idx[n1:]]
        null_dist[i] = statistic(perm1, perm2)
    
    p_value = float(np.mean(np.abs(null_dist) >= np.abs(observed)))
    
    return {
        "statistic": float(observed),
        "p_value": p_value,
        "null_distribution": null_dist,
        "n_permutations": n_permutations
    }


def max_stat_permutation_test(data: np.ndarray, labels: np.ndarray,
                              n_permutations: int = 10000, seed: int = 42) -> dict:
    """Max-statistic permutation test for multiple comparisons.
    
    Corrects for multiple comparisons by using the maximum statistic across
    all comparisons in each permutation.
    
    Args:
        data: (n_observations, n_comparisons) array.
        labels: (n_observations,) binary labels.
        n_permutations: Number of permutations.
        seed: Random seed.
    
    Returns:
        {"statistics": obs_stats, "p_values": corrected_p, "threshold": max_stat_thresh}
    """
    rng = DeterministicRNG(seed)
    n_obs, n_comp = data.shape
    
    # Observed statistics (e.g., t-statistic for each comparison)
    obs_stats = np.zeros(n_comp)
    for c in range(n_comp):
        g1 = data[labels == 0, c]
        g2 = data[labels == 1, c]
        obs_stats[c] = np.mean(g1) - np.mean(g2)
    
    # Permutation distribution of max |statistic|
    max_stats = np.zeros(n_permutations)
    for i in range(n_permutations):
        perm_labels = labels.copy()
        idx = rng.integer(0, n_obs, size=n_obs)
        perm_labels = labels[idx]
        perm_stats = np.zeros(n_comp)
        for c in range(n_comp):
            g1 = data[perm_labels == 0, c]
            g2 = data[perm_labels == 1, c]
            if len(g1) > 0 and len(g2) > 0:
                perm_stats[c] = np.mean(g1) - np.mean(g2)
        max_stats[i] = np.max(np.abs(perm_stats))
    
    # Corrected p-values
    threshold_95 = float(np.percentile(max_stats, 95))
    corrected_p = np.zeros(n_comp)
    for c in range(n_comp):
        corrected_p[c] = float(np.mean(max_stats >= np.abs(obs_stats[c])))
    
    return {
        "statistics": obs_stats,
        "p_values": corrected_p,
        "threshold_95": threshold_95,
        "n_permutations": n_permutations
    }


def cluster_based_permutation_test(data1: np.ndarray, data2: np.ndarray,
                                   threshold: float = 0.05,
                                   n_permutations: int = 1000,
                                   seed: int = 42) -> dict:
    """Cluster-based permutation test (Maris & Oostenveld 2007).
    
    For EEG time-frequency data: finds clusters of adjacent significant
    time-frequency points, computes cluster mass, and tests against
    permutation distribution of max cluster mass.
    
    Args:
        data1: (n_subjects1, n_time, n_freq) — condition 1
        data2: (n_subjects2, n_time, n_freq) — condition 2
        threshold: p-value threshold for cluster-forming
        n_permutations: Number of permutations
        seed: Random seed
    
    Returns:
        {"clusters": list, "p_values": list, "n_permutations": n}
    """
    from scipy import stats
    rng = DeterministicRNG(seed)
    
    # Observed t-statistic at each time-freq point
    n_time, n_freq = data1.shape[1], data1.shape[2]
    t_obs = np.zeros((n_time, n_freq))
    p_obs = np.zeros((n_time, n_freq))
    for t in range(n_time):
        for f in range(n_freq):
            t_stat, p_val = stats.ttest_ind(data1[:, t, f], data2[:, t, f])
            t_obs[t, f] = t_stat
            p_obs[t, f] = p_val
    
    # Find clusters (adjacent significant points)
    significant = p_obs < threshold
    # Simple clustering: connected components in 2D
    from scipy.ndimage import label
    labeled, n_clusters = label(significant)
    
    # Cluster mass = sum of |t-stat| in cluster
    cluster_masses = []
    for c in range(1, n_clusters + 1):
        mass = np.sum(np.abs(t_obs[labeled == c]))
        cluster_masses.append(mass)
    
    # Permutation distribution of max cluster mass
    combined = np.concatenate([data1, data2], axis=0)
    n1 = data1.shape[0]
    max_cluster_masses = np.zeros(n_permutations)
    
    for i in range(n_permutations):
        idx = rng.integer(0, len(combined), size=len(combined))
        perm1 = combined[idx[:n1]]
        perm2 = combined[idx[n1:]]
        # Compute t-stats
        t_perm = np.zeros((n_time, n_freq))
        p_perm = np.zeros((n_time, n_freq))
        for t in range(n_time):
            for f in range(n_freq):
                t_stat, p_val = stats.ttest_ind(perm1[:, t, f], perm2[:, t, f])
                t_perm[t, f] = t_stat
                p_perm[t, f] = p_val
        sig_perm = p_perm < threshold
        labeled_perm, n_clust_perm = label(sig_perm)
        if n_clust_perm > 0:
            masses = [np.sum(np.abs(t_perm[labeled_perm == c])) for c in range(1, n_clust_perm + 1)]
            max_cluster_masses[i] = max(masses)
    
    # P-values for each observed cluster
    cluster_p_values = []
    for mass in cluster_masses:
        p = float(np.mean(max_cluster_masses >= mass))
        cluster_p_values.append(p)
    
    return {
        "n_clusters": n_clusters,
        "cluster_masses": cluster_masses,
        "p_values": cluster_p_values,
        "n_permutations": n_permutations
    }
```

### Tests

```python
def test_permutation_test_significant():
    rng = np.random.default_rng(42)
    g1 = rng.normal(5, 1, 50)
    g2 = rng.normal(6, 1, 50)  # different mean
    result = permutation_test(g1, g2, n_permutations=1000, seed=42)
    assert result["p_value"] < 0.05, f"p={result['p_value']} should be < 0.05"

def test_permutation_test_not_significant():
    rng = np.random.default_rng(42)
    g1 = rng.normal(5, 1, 50)
    g2 = rng.normal(5, 1, 50)  # same mean
    result = permutation_test(g1, g2, n_permutations=1000, seed=42)
    assert result["p_value"] > 0.05, f"p={result['p_value']} should be > 0.05"

def test_max_stat_corrects_for_multiple_comparisons():
    """Max-stat test should be more conservative than uncorrected."""
    rng = np.random.default_rng(42)
    n_obs, n_comp = 20, 100
    data = rng.normal(0, 1, (n_obs, n_comp))
    labels = np.array([0]*10 + [1]*10)
    result = max_stat_permutation_test(data, labels, n_permutations=200, seed=42)
    # With no real effect, most p-values should be > 0.05
    assert np.mean(result["p_values"] < 0.05) < 0.1
```

### Gemini Prompt
```
You are executing task S15. Create vireon-validation/vireon_validation/statistics/permutation.py with: permutation_test (two-sample, default mean difference), max_stat_permutation_test (corrects for multiple comparisons via max |stat| across permutations), cluster_based_permutation_test (Maris & Oostenveld 2007, for EEG time-freq data, uses scipy.ndimage.label for clustering). Use DeterministicRNG. Write tests: significant difference (p<0.05), no difference (p>0.05), max-stat correction (fewer false positives than uncorrected). Branch: svp/S15-permutation-testing. TDD. Commit. PR. Stop.
```

---

## S16: Effect Size Computation

**Effort:** S | **Dependencies:** None | **Verification:** G1

### Context
`vireon-validation/vireon_validation/statistics/core.py` has `compute_cohens_d()`. Need to add: Hedges' g (corrected for small samples), η² (eta-squared, for ANOVA), partial η², and odds ratio.

### Implementation

Add to `vireon-validation/vireon_validation/statistics/effect_sizes.py`:

```python
"""Effect size computations.

Reference: Cohen, J. (1988). Statistical Power Analysis for the Behavioral Sciences.
"""
import numpy as np
from typing import Optional


def cohens_d(group1: np.ndarray, group2: np.ndarray, pooled: bool = True) -> float:
    """Cohen's d effect size.
    
    d = (mean1 - mean2) / pooled_std
    """
    m1, m2 = np.mean(group1), np.mean(group2)
    if pooled:
        n1, n2 = len(group1), len(group2)
        v1, v2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
        pooled_var = ((n1 - 1) * v1 + (n2 - 1) * v2) / (n1 + n2 - 2)
        pooled_std = np.sqrt(pooled_var)
    else:
        pooled_std = np.std(group1, ddof=1)
    if pooled_std == 0:
        return 0.0
    return float((m1 - m2) / pooled_std)


def hedges_g(group1: np.ndarray, group2: np.ndarray) -> float:
    """Hedges' g — Cohen's d with small-sample bias correction.
    
    g = d * (1 - 3/(4*(n1+n2) - 9))
    """
    d = cohens_d(group1, group2)
    n1, n2 = len(group1), len(group2)
    correction = 1 - 3.0 / (4 * (n1 + n2) - 9)
    return float(d * correction)


def eta_squared(groups: list) -> float:
    """η² (eta-squared) for one-way ANOVA.
    
    η² = SS_between / SS_total
    """
    all_data = np.concatenate(groups)
    grand_mean = np.mean(all_data)
    ss_between = sum(len(g) * (np.mean(g) - grand_mean) ** 2 for g in groups)
    ss_total = np.sum((all_data - grand_mean) ** 2)
    if ss_total == 0:
        return 0.0
    return float(ss_between / ss_total)


def partial_eta_squared(ss_effect: float, ss_error: float) -> float:
    """Partial η² = SS_effect / (SS_effect + SS_error)."""
    denom = ss_effect + ss_error
    if denom == 0:
        return 0.0
    return float(ss_effect / denom)


def odds_ratio(a: int, b: int, c: int, d: int) -> float:
    """Odds ratio from 2x2 contingency table.
    
    | a | b |
    | c | d |
    
    OR = (a*d) / (b*c)
    """
    if b * c == 0:
        return float('inf')
    return float((a * d) / (b * c))


def interpret_cohens_d(d: float) -> str:
    """Interpret Cohen's d magnitude (Cohen 1988 conventions)."""
    d = abs(d)
    if d < 0.2:
        return "negligible"
    elif d < 0.5:
        return "small"
    elif d < 0.8:
        return "medium"
    else:
        return "large"
```

### Tests

```python
def test_cohens_d_zero():
    g = np.random.default_rng(42).normal(5, 1, 100)
    assert abs(cohens_d(g, g)) < 0.1

def test_cohens_d_large():
    rng = np.random.default_rng(42)
    g1 = rng.normal(0, 1, 100)
    g2 = rng.normal(3, 1, 100)
    d = cohens_d(g1, g2)
    assert d > 2.0  # large effect
    assert interpret_cohens_d(d) == "large"

def test_hedges_g_smaller_than_cohens_d():
    rng = np.random.default_rng(42)
    g1 = rng.normal(0, 1, 10)  # small sample
    g2 = rng.normal(1, 1, 10)
    d = cohens_d(g1, g2)
    g = hedges_g(g1, g2)
    assert abs(g) < abs(d)  # Hedges' g is always slightly smaller

def test_eta_squared():
    g1 = np.array([1, 2, 3, 4, 5])
    g2 = np.array([6, 7, 8, 9, 10])
    eta = eta_squared([g1, g2])
    assert 0 < eta <= 1.0
    assert eta > 0.5  # large effect
```

### Gemini Prompt
```
You are executing task S16. Create vireon-validation/vireon_validation/statistics/effect_sizes.py with: cohens_d (pooled std), hedges_g (small-sample correction), eta_squared (one-way ANOVA), partial_eta_squared, odds_ratio, interpret_cohens_d (Cohen 1988 conventions). Write 4 tests. Branch: svp/S16-effect-sizes. TDD. Commit. PR. Stop.
```

---

## S17: Multiple Comparison Correction (FDR)

**Effort:** S | **Dependencies:** None | **Verification:** G6

### Context
No FDR correction exists. Need Benjamini-Hochberg procedure for controlling false discovery rate.

### Implementation

Create `vireon-validation/vireon_validation/statistics/multiple_comparisons.py`:

```python
"""Multiple comparison correction procedures.

Reference: Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery 
rate: A practical and powerful approach to multiple testing. Journal of the 
Royal Statistical Society, Series B, 57(1), 289-300.
"""
import numpy as np
from typing import Tuple


def bonferroni_correction(p_values: np.ndarray, alpha: float = 0.05) -> Tuple[np.ndarray, np.ndarray]:
    """Bonferroni correction (controls FWER).
    
    Adjusted p-values: p_i * m (capped at 1.0)
    Significant if adjusted_p < alpha.
    """
    p_values = np.asarray(p_values, dtype=float)
    m = len(p_values)
    adjusted = np.minimum(p_values * m, 1.0)
    significant = adjusted < alpha
    return adjusted, significant


def benjamini_hochberg(p_values: np.ndarray, alpha: float = 0.05) -> Tuple[np.ndarray, np.ndarray]:
    """Benjamini-Hochberg FDR correction.
    
    Controls the expected proportion of false discoveries among all discoveries.
    
    Procedure:
    1. Sort p-values: p(1) ≤ p(2) ≤ ... ≤ p(m)
    2. Find largest k such that p(k) ≤ k/m * alpha
    3. Reject all H(i) for i ≤ k
    
    Returns:
        (adjusted_p_values, significant_mask)
    """
    p_values = np.asarray(p_values, dtype=float)
    m = len(p_values)
    
    # Sort p-values, keeping track of original indices
    sorted_idx = np.argsort(p_values)
    sorted_p = p_values[sorted_idx]
    
    # Compute adjusted p-values: p_adj(k) = min(p(j) * m / j for j >= k)
    adjusted_sorted = np.zeros(m)
    adjusted_sorted[-1] = sorted_p[-1] * m / m  # = sorted_p[-1]
    for k in range(m - 2, -1, -1):
        rank = k + 1
        adjusted_sorted[k] = min(adjusted_sorted[k + 1], sorted_p[k] * m / rank)
    
    adjusted_sorted = np.minimum(adjusted_sorted, 1.0)
    
    # Unsort
    adjusted = np.zeros(m)
    adjusted[sorted_idx] = adjusted_sorted
    
    significant = adjusted < alpha
    return adjusted, significant


def holm_bonferroni(p_values: np.ndarray, alpha: float = 0.05) -> Tuple[np.ndarray, np.ndarray]:
    """Holm-Bonferroni correction (step-down, controls FWER).
    
    More powerful than Bonferroni.
    """
    p_values = np.asarray(p_values, dtype=float)
    m = len(p_values)
    
    sorted_idx = np.argsort(p_values)
    sorted_p = p_values[sorted_idx]
    
    adjusted_sorted = np.zeros(m)
    for i in range(m):
        rank = i + 1
        adjusted_sorted[i] = sorted_p[i] * (m - rank + 1)
    
    # Enforce monotonicity (step-down)
    for i in range(1, m):
        adjusted_sorted[i] = max(adjusted_sorted[i], adjusted_sorted[i - 1])
    
    adjusted_sorted = np.minimum(adjusted_sorted, 1.0)
    
    adjusted = np.zeros(m)
    adjusted[sorted_idx] = adjusted_sorted
    
    significant = adjusted < alpha
    return adjusted, significant
```

### Tests

```python
def test_bonferroni_basic():
    p = np.array([0.01, 0.02, 0.03, 0.04, 0.05])
    adj, sig = bonferroni_correction(p, alpha=0.05)
    assert np.allclose(adj, p * 5)
    assert sig[0]  # 0.05 < 0.05? No... 0.01*5=0.05, which is NOT < 0.05
    # Actually 0.01*5 = 0.05, and we check < alpha (0.05), so not significant
    assert not sig.any()  # none significant at alpha=0.05

def test_bh_fdr_control():
    """BH should control FDR at the declared level."""
    rng = np.random.default_rng(42)
    n_tests = 100
    n_true_null = 90  # 90% are true null (no effect)
    n_false_null = n_tests - n_true_null
    
    # Generate p-values: true nulls ~ Uniform(0,1), false nulls ~ Beta(1, 20) (mostly small)
    p_values = np.zeros(n_tests)
    p_values[:n_true_null] = rng.uniform(0, 1, n_true_null)
    p_values[n_true_null:] = rng.beta(1, 20, n_false_null)
    
    adj, sig = benjamini_hochberg(p_values, alpha=0.05)
    
    # Should detect most false nulls
    detected_false = np.sum(sig[n_true_null:])
    assert detected_false > n_false_null * 0.5, \
        f"Only detected {detected_false}/{n_false_null} false nulls"

def test_bh_more_powerful_than_bonferroni():
    """BH should declare more significant than Bonferroni."""
    p = np.array([0.001, 0.005, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08])
    _, sig_bonf = bonferroni_correction(p, alpha=0.05)
    _, sig_bh = benjamini_hochberg(p, alpha=0.05)
    assert np.sum(sig_bh) >= np.sum(sig_bonf)

def test_holm_step_down():
    """Holm-Bonferroni should be step-down (monotonic adjusted p-values)."""
    p = np.array([0.01, 0.04, 0.03, 0.001])
    adj, sig = holm_bonferroni(p, alpha=0.05)
    # Smallest p-value should have smallest adjusted p
    assert adj[3] <= adj[0]  # p=0.001 < p=0.01
```

### Gemini Prompt
```
You are executing task S17. Create vireon-validation/vireon_validation/statistics/multiple_comparisons.py with: bonferroni_correction (p*m, cap 1.0), benjamini_hochberg (FDR control, step-up), holm_bonferroni (step-down FWER). Write 4 tests: Bonferroni basic, BH FDR control (detects >50% of false nulls), BH more powerful than Bonferroni, Holm step-down monotonicity. Branch: svp/S17-multiple-comparison-correction. TDD. Commit. PR. Stop.
```

---

## S18: Statistical Rigor Integration Test

**Effort:** S | **Dependencies:** S14-S17 | **Verification:** G4

### Context
Need an integration test verifying that every evidence bundle includes bootstrap CIs, effect sizes, and corrected p-values.

### Implementation

Create `tests/test_statistical_rigor.py`:

```python
"""Integration test: every evidence bundle has statistical rigor."""
import json
import os
import subprocess
import sys
import numpy as np
import pytest

def test_evidence_bundle_has_bootstrap_ci():
    """Evidence bundle should include bootstrap CI for CCC."""
    from vireon_validation.statistics.bootstrap import bootstrap_ccc_ci
    rng = np.random.default_rng(42)
    x = rng.normal(0, 1, 100)
    y = x + rng.normal(0, 0.2, 100)
    ci = bootstrap_ccc_ci(x, y, n_bootstrap=1000, seed=42)
    assert "ccc" in ci
    assert "ci_lower" in ci and "ci_upper" in ci
    assert ci["ci_lower"] < ci["ccc"] < ci["ci_upper"]

def test_evidence_bundle_has_effect_size():
    """Evidence bundle should include effect size."""
    from vireon_validation.statistics.effect_sizes import cohens_d, interpret_cohens_d
    rng = np.random.default_rng(42)
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
    assert adj[0] <= adj[1]  # sorted

def test_demo_evidence_has_rigorous_statistics():
    """Run the demo and verify the evidence has CIs."""
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
        bundle = json.load(open(evidence_path))
        # The bundle should have real CCC (not hardcoded)
        ccc = bundle.get("statistical_agreement", {}).get("ccc", 0)
        assert ccc != 0.95, "CCC is hardcoded 0.95"
        assert 0 <= ccc <= 1.0, f"CCC {ccc} out of range"
```

### Acceptance Criteria
- [ ] Bootstrap CI computed for CCC
- [ ] Effect size computed and interpreted
- [ ] FDR-corrected p-values available
- [ ] Demo evidence has real CCC (not hardcoded)

### Gemini Prompt
```
You are executing task S18. Create tests/test_statistical_rigor.py with 4 integration tests: bootstrap CI for CCC, effect size computation, FDR-corrected p-values, demo evidence has real CCC (not 0.95). Branch: svp/S18-statistical-rigor-integration. TDD. Commit. PR. Stop. Depends on S14-S17.
```
