"""
FDRCorrection — Benjamini-Hochberg FDR correction.

Reference: Benjamini, Y., & Hochberg, Y. (1995). Controlling the false
discovery rate: A practical and powerful approach to multiple testing.
Journal of the Royal Statistical Society, Series B, 57(1), 289-300.

Procedure:
  1. Sort p-values ascending: p(1) <= p(2) <= ... <= p(m)
  2. For each rank k (1-indexed), threshold: p(k) <= (k / m) * alpha
  3. Find the largest k for which this holds; reject H0 for all p(1..k).
  4. If no k satisfies the condition, reject nothing.

The `correct` static method returns a boolean numpy array — True for
hypotheses that survive FDR correction at the given alpha.
"""
from __future__ import annotations

from typing import Any

import numpy as np


class FDRCorrection:
    """Benjamini-Hochberg FDR correction."""

    @staticmethod
    def correct(p_values: np.ndarray, alpha: float = 0.05) -> np.ndarray:
        """Apply BH FDR correction and return a boolean mask of rejections.

        Args:
            p_values: 1D array of p-values (any shape will be flattened).
            alpha: Target false discovery rate (default 0.05).

        Returns:
            1D boolean array of same length as input. True = reject H0 for
            that hypothesis (i.e., the p-value survives FDR correction).
        """
        p = np.asarray(p_values, dtype=np.float64).ravel()
        m = p.size
        if m == 0:
            return np.array([], dtype=bool)
        if alpha <= 0 or alpha >= 1:
            raise ValueError(f"alpha must be in (0, 1); got {alpha}")

        # Sort p-values ascending, keep original indices
        sorted_idx = np.argsort(p, kind="stable")
        sorted_p = p[sorted_idx]

        # BH thresholds: (k / m) * alpha for k = 1..m
        ranks = np.arange(1, m + 1, dtype=np.float64)
        thresholds = (ranks / m) * alpha

        # Find the largest k for which p(k) <= threshold(k)
        # = the largest index where sorted_p <= thresholds
        pass_mask = sorted_p <= thresholds
        if not pass_mask.any():
            return np.zeros(m, dtype=bool)

        # Reject all p(1..k*) where k* is the largest passing rank
        k_star = int(np.max(np.where(pass_mask)[0]))  # 0-indexed
        rejected_sorted = np.zeros(m, dtype=bool)
        rejected_sorted[: k_star + 1] = True

        # Map back to original order
        rejected = np.zeros(m, dtype=bool)
        rejected[sorted_idx] = rejected_sorted
        return rejected

    @staticmethod
    def adjusted_pvalues(p_values: np.ndarray) -> np.ndarray:
        """Compute BH-adjusted p-values (q-values).

        q(k) = min over j >= k of (p(j) * m / j), capped at 1.0.

        Returns:
            1D array of adjusted p-values in the ORIGINAL order.
        """
        p = np.asarray(p_values, dtype=np.float64).ravel()
        m = p.size
        if m == 0:
            return np.array([], dtype=np.float64)
        sorted_idx = np.argsort(p, kind="stable")
        sorted_p = p[sorted_idx]
        ranks = np.arange(1, m + 1, dtype=np.float64)
        adjusted_sorted = sorted_p * m / ranks
        # Enforce monotonicity from the right (min over j >= k)
        for k in range(m - 2, -1, -1):
            adjusted_sorted[k] = min(adjusted_sorted[k], adjusted_sorted[k + 1])
        adjusted_sorted = np.minimum(adjusted_sorted, 1.0)
        # Unsort
        out = np.zeros(m, dtype=np.float64)
        out[sorted_idx] = adjusted_sorted
        return out


__all__ = ["FDRCorrection"]
