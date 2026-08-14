"""
Effect-size computations: Cohen's d and Glass's delta.

Reference: Cohen, J. (1988). Statistical Power Analysis for the Behavioral
Sciences. Lawrence Erlbaum Associates.

- Cohen's d uses the POOLED standard deviation of both groups.
- Glass's delta uses the standard deviation of a CONTROL / reference group
  only (group2 by convention here), which is preferable when the treatment
  group's variance is itself affected by the intervention.

Both are static-method classes for symmetry with the rest of the statistics
subpackage.
"""
from __future__ import annotations

from typing import Any

import numpy as np


class CohensD:
    """Cohen's d effect size (pooled-SD form).

    d = (mean1 - mean2) / pooled_std
        where pooled_std = sqrt(((n1-1)*s1^2 + (n2-1)*s2^2) / (n1+n2-2))
    """

    @staticmethod
    def compute(group1: np.ndarray, group2: np.ndarray) -> float:
        """Compute Cohen's d between two groups.

        Args:
            group1, group2: 1D arrays of observations.

        Returns:
            Cohen's d (float). 0.0 if both groups have zero variance.
        """
        g1 = np.asarray(group1, dtype=np.float64).ravel()
        g2 = np.asarray(group2, dtype=np.float64).ravel()
        m1, m2 = float(g1.mean()), float(g2.mean())
        n1, n2 = g1.size, g2.size
        if n1 + n2 < 2:
            # Pooled variance undefined with < 2 total observations
            return 0.0
        v1 = float(g1.var(ddof=1)) if n1 > 1 else 0.0
        v2 = float(g2.var(ddof=1)) if n2 > 1 else 0.0
        pooled_var = ((n1 - 1) * v1 + (n2 - 1) * v2) / (n1 + n2 - 2)
        pooled_std = float(np.sqrt(pooled_var))
        if pooled_std == 0.0:
            return 0.0
        return float((m1 - m2) / pooled_std)


class GlassDelta:
    """Glass's delta effect size (control-group SD).

    delta = (mean1 - mean2) / std(group2)

    `group2` is treated as the CONTROL / reference group; its standard
    deviation is used as the denominator. This is preferable to Cohen's d
    when the treatment is expected to change the variance of the experimental
    group.
    """

    @staticmethod
    def compute(group1: np.ndarray, group2: np.ndarray) -> float:
        """Compute Glass's delta between two groups (group2 = control).

        Args:
            group1: Treatment group observations.
            group2: Control group observations (whose SD is used).

        Returns:
            Glass's delta (float). 0.0 if control group has zero variance or
            fewer than 2 observations.
        """
        g1 = np.asarray(group1, dtype=np.float64).ravel()
        g2 = np.asarray(group2, dtype=np.float64).ravel()
        if g2.size < 2:
            return 0.0
        m1, m2 = float(g1.mean()), float(g2.mean())
        control_std = float(g2.std(ddof=1))
        if control_std == 0.0:
            return 0.0
        return float((m1 - m2) / control_std)


__all__ = ["CohensD", "GlassDelta"]
