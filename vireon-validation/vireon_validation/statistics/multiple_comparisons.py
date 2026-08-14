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
    1. Sort p-values: p(1) <= p(2) <= ... <= p(m)
    2. Adjusted p-values: p_adj(k) = min(p(j) * m / j for j >= k)
    3. Significant if adjusted_p < alpha

    Returns:
        (adjusted_p_values, significant_mask)
    """
    p_values = np.asarray(p_values, dtype=float)
    m = len(p_values)
    if m == 0:
        return np.array([]), np.array([], dtype=bool)

    # Sort p-values, keeping track of original indices
    sorted_idx = np.argsort(p_values)
    sorted_p = p_values[sorted_idx]

    # Compute adjusted p-values: p_adj(k) = min(p(j) * m / j for j >= k)
    adjusted_sorted = np.zeros(m)
    adjusted_sorted[-1] = sorted_p[-1] * m / m
    for k in range(m - 2, -1, -1):
        rank = k + 1
        adjusted_sorted[k] = min(adjusted_sorted[k + 1], sorted_p[k] * m / rank)

    adjusted_sorted = np.minimum(adjusted_sorted, 1.0)

    # Unsort to original order
    adjusted = np.zeros(m)
    adjusted[sorted_idx] = adjusted_sorted

    significant = adjusted < alpha
    return adjusted, significant


def holm_bonferroni(p_values: np.ndarray, alpha: float = 0.05) -> Tuple[np.ndarray, np.ndarray]:
    """Holm-Bonferroni correction (step-down, controls FWER).

    More powerful than standard Bonferroni.
    """
    p_values = np.asarray(p_values, dtype=float)
    m = len(p_values)
    if m == 0:
        return np.array([]), np.array([], dtype=bool)

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
