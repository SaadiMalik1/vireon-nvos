"""Effect size computations.

Reference: Cohen, J. (1988). Statistical Power Analysis for the Behavioral Sciences.
"""
import numpy as np
from typing import Optional, List


def cohens_d(group1: np.ndarray, group2: np.ndarray, pooled: bool = True) -> float:
    """Cohen's d effect size.

    d = (mean1 - mean2) / pooled_std
    """
    group1 = np.asarray(group1, dtype=float).ravel()
    group2 = np.asarray(group2, dtype=float).ravel()
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

    g = d * (1 - 3 / (4 * (n1 + n2) - 9))
    """
    d = cohens_d(group1, group2)
    n1, n2 = len(group1), len(group2)
    correction = 1.0 - 3.0 / (4.0 * (n1 + n2) - 9.0)
    return float(d * correction)


def eta_squared(groups: List[np.ndarray]) -> float:
    """η² (eta-squared) for one-way ANOVA.

    η² = SS_between / SS_total
    """
    all_data = np.concatenate([np.asarray(g, dtype=float).ravel() for g in groups])
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

    OR = (a * d) / (b * c)
    """
    if b * c == 0:
        return float('inf')
    return float((a * d) / (b * c))


def interpret_cohens_d(d: float) -> str:
    """Interpret Cohen's d magnitude (Cohen 1988 conventions)."""
    val = abs(d)
    if val < 0.2:
        return "negligible"
    elif val < 0.5:
        return "small"
    elif val < 0.8:
        return "medium"
    else:
        return "large"
