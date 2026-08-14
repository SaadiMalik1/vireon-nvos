"""
SubjectLevelPermutation — permutation test for above-chance accuracy.

Per ADR 0008 #5: VIREON permutation tests respect experimental structure.
For "is the pipeline better than chance?" we test the SUBJECT-level mean
accuracy against `chance_level` (e.g., 0.5 for binary classification).

Hypothesis:
  H0: subject accuracies are drawn from a distribution with mean = chance_level
  H1: subject accuracies are drawn from a distribution with mean > chance_level
      (one-sided test — we only care about "above chance").

Procedure:
  1. Center accuracies at chance: shifted = accs - mean(accs) + chance_level
     (this puts the observed mean at chance under H0, preserving variance).
  2. Observed statistic: T_obs = mean(accs) - chance_level
  3. For each permutation: shuffle the shifted accuracies, compute
     T_perm = mean(permuted) - chance_level
  4. p_value = (1 + #{T_perm >= T_obs}) / (1 + n_permutations)
     (the +1 in numerator and denominator is the standard add-one correction
     to avoid p = 0).

Reference: Nichols, T. E., & Holmes, A. P. (2002). Nonparametric permutation
tests for functional neuroimaging. Human Brain Mapping, 15(1), 1-25.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass
class PermutationResult:
    """Result of a subject-level permutation test against chance."""
    observed_statistic: float
    p_value: float
    n_permutations: int
    significant: bool
    alpha: float = 0.05
    chance_level: float = 0.5
    unit: str = "subject"
    observed_mean: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "observed_statistic": self.observed_statistic,
            "p_value": self.p_value,
            "n_permutations": self.n_permutations,
            "significant": self.significant,
            "alpha": self.alpha,
            "chance_level": self.chance_level,
            "observed_mean": self.observed_mean,
            "unit": self.unit,
        }

    def __repr__(self) -> str:
        sig = "SIGNIFICANT" if self.significant else "n.s."
        return (
            f"PermutationResult(obs={self.observed_statistic:.4f}, "
            f"p={self.p_value:.4f}, n_perm={self.n_permutations}, "
            f"alpha={self.alpha}, {sig}, unit='{self.unit}')"
        )


class SubjectLevelPermutation:
    """One-sided permutation test: is mean accuracy above chance?

    Usage:
        perm = SubjectLevelPermutation(n_permutations=1000, seed=42, alpha=0.05)
        result = perm.test_above_chance(subject_accuracies, chance_level=0.5)
        print(result.p_value, result.significant)
    """

    def __init__(self, n_permutations: int = 1000, seed: int = 42, alpha: float = 0.05):
        if n_permutations < 1:
            raise ValueError(f"n_permutations must be >= 1; got {n_permutations}")
        if not (0.0 < alpha < 1.0):
            raise ValueError(f"alpha must be in (0, 1); got {alpha}")
        self.n_permutations = int(n_permutations)
        self.seed = int(seed)
        self.alpha = float(alpha)

    def test_above_chance(
        self,
        subject_accuracies: np.ndarray,
        chance_level: float = 0.5,
    ) -> PermutationResult:
        """Test whether mean subject-level accuracy > chance_level.

        Args:
            subject_accuracies: 1D array of per-subject accuracies.
            chance_level: Null-hypothesis mean (e.g., 0.5 for binary, 1/n_classes
                for multi-class).

        Returns:
            PermutationResult with observed statistic, p-value, and significance.
        """
        accs = np.asarray(subject_accuracies, dtype=np.float64).ravel()
        n = accs.size
        if n == 0:
            return PermutationResult(
                observed_statistic=float("nan"),
                p_value=1.0,
                n_permutations=self.n_permutations,
                significant=False,
                alpha=self.alpha,
                chance_level=float(chance_level),
                observed_mean=float("nan"),
                unit="subject",
            )

        observed_mean = float(accs.mean())
        observed_stat = observed_mean - float(chance_level)

        # Center accuracies at chance under H0:
        # shifted = accs - observed_mean + chance_level
        # → mean(shifted) = chance_level, variance preserved.
        shifted = accs - observed_mean + float(chance_level)

        rng = np.random.default_rng(self.seed)
        count_ge = 0
        for _ in range(self.n_permutations):
            rng.shuffle(shifted)
            t_perm = shifted.mean() - float(chance_level)
            if t_perm >= observed_stat:
                count_ge += 1

        # Add-one correction (avoids p=0)
        p_value = (count_ge + 1) / (self.n_permutations + 1)
        significant = bool(p_value < self.alpha)

        return PermutationResult(
            observed_statistic=float(observed_stat),
            p_value=float(p_value),
            n_permutations=self.n_permutations,
            significant=significant,
            alpha=self.alpha,
            chance_level=float(chance_level),
            observed_mean=observed_mean,
            unit="subject",
        )


__all__ = ["SubjectLevelPermutation", "PermutationResult"]
