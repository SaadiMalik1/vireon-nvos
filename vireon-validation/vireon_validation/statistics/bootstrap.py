"""Bootstrap confidence intervals for all metrics.

Reference: Efron, B., & Tibshirani, R. J. (1994). An Introduction to the Bootstrap.
Chapman & Hall/CRC.
"""
import numpy as np
from typing import Callable, Tuple, Optional, Dict, Any
from vireon_core.runtime.rng import DeterministicRNG


def bootstrap_ci(
    data: np.ndarray,
    statistic: Callable,
    n_bootstrap: int = 10000,
    confidence: float = 0.95,
    seed: int = 42
) -> Tuple[float, float, float]:
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
    data = np.asarray(data)
    rng = DeterministicRNG(seed)
    n = len(data)
    point_estimate = statistic(data)

    boot_stats = np.zeros(n_bootstrap)
    for i in range(n_bootstrap):
        idx = rng.integer(0, n, size=n)
        boot_sample = data[idx] if data.ndim == 1 else data[idx, :]
        boot_stats[i] = statistic(boot_sample)

    alpha = (1.0 - confidence) / 2.0
    ci_lower = float(np.percentile(boot_stats, 100.0 * alpha))
    ci_upper = float(np.percentile(boot_stats, 100.0 * (1.0 - alpha)))

    return float(point_estimate), ci_lower, ci_upper


def compute_bootstrap_ci(
    data: np.ndarray,
    statistic_fn: Callable,
    n_resamples: int = 1000,
    seed: int = 42,
    **kwargs
) -> Tuple[float, float, list[float]]:
    """Compute point estimate, variance, and 95% bootstrap CI for legacy callers."""
    point_est, ci_l, ci_u = bootstrap_ci(data, statistic_fn, n_bootstrap=n_resamples, seed=seed)
    var = float((ci_u - ci_l) ** 2 / 3.8416) if ci_u != ci_l else 0.0
    return point_est, var, [ci_l, ci_u]


def bootstrap_ccc_ci(
    x: np.ndarray,
    y: np.ndarray,
    n_bootstrap: int = 10000,
    confidence: float = 0.95,
    seed: int = 42
) -> Dict[str, Any]:
    """Bootstrap CI for Lin's Concordance Correlation Coefficient."""
    from vireon_validation.statistics.framework import lin_concordance_correlation

    x = np.asarray(x).ravel()
    y = np.asarray(y).ravel()
    data = np.column_stack([x, y])

    def calc_ccc(d):
        return lin_concordance_correlation(d[:, 0], d[:, 1])

    point, ci_lo, ci_hi = bootstrap_ci(
        data, calc_ccc, n_bootstrap=n_bootstrap, confidence=confidence, seed=seed
    )
    return {"ccc": point, "ci_lower": ci_lo, "ci_upper": ci_hi, "confidence": confidence}


def bootstrap_accuracy_ci(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    n_bootstrap: int = 10000,
    confidence: float = 0.95,
    seed: int = 42
) -> Dict[str, Any]:
    """Bootstrap CI for classification accuracy."""
    from sklearn.metrics import accuracy_score

    y_true = np.asarray(y_true).ravel()
    y_pred = np.asarray(y_pred).ravel()
    data = np.column_stack([y_true, y_pred])

    def calc_acc(d):
        return accuracy_score(d[:, 0], d[:, 1])

    point, ci_lo, ci_hi = bootstrap_ci(
        data, calc_acc, n_bootstrap=n_bootstrap, confidence=confidence, seed=seed
    )
    return {"accuracy": point, "ci_lower": ci_lo, "ci_upper": ci_hi, "confidence": confidence}


def bootstrap_rmse_ci(
    x: np.ndarray,
    y: np.ndarray,
    n_bootstrap: int = 10000,
    confidence: float = 0.95,
    seed: int = 42
) -> Dict[str, Any]:
    """Bootstrap CI for RMSE."""
    x = np.asarray(x).ravel()
    y = np.asarray(y).ravel()
    data = np.column_stack([x, y])

    def calc_rmse(d):
        return float(np.sqrt(np.mean((d[:, 0] - d[:, 1]) ** 2)))

    point, ci_lo, ci_hi = bootstrap_ci(
        data, calc_rmse, n_bootstrap=n_bootstrap, confidence=confidence, seed=seed
    )
    return {"rmse": point, "ci_lower": ci_lo, "ci_upper": ci_hi, "confidence": confidence}
