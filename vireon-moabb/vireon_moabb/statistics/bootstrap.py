"""
SubjectLevelBootstrap — bootstrap CI for subject-level accuracies.

Per ADR 0008 #5: VIREON bootstraps at the SUBJECT level, not trial level.
Resampling individual trials creates pseudoreplication — observations within
a subject aren't independent. With small N (e.g., BNCI2014_001 has 9 subjects),
subject-level bootstrap is the correct unit.

Reference: Efron, B., & Tibshirani, R. J. (1994). An Introduction to the
Bootstrap. Chapman & Hall/CRC.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass
class BootstrapResult:
    """Result of a subject-level bootstrap."""
    mean: float
    std: float
    ci_lower: float
    ci_upper: float
    ci_level: float
    n_bootstrap: int
    n_observations: int
    unit: str = "subject"

    def to_dict(self) -> dict[str, Any]:
        return {
            "mean": self.mean,
            "std": self.std,
            "ci_lower": self.ci_lower,
            "ci_upper": self.ci_upper,
            "ci_level": self.ci_level,
            "n_bootstrap": self.n_bootstrap,
            "n_observations": self.n_observations,
            "unit": self.unit,
        }

    def __repr__(self) -> str:
        return (
            f"BootstrapResult(mean={self.mean:.4f}, std={self.std:.4f}, "
            f"CI=[{self.ci_lower:.4f}, {self.ci_upper:.4f}] @ {self.ci_level:.0%}, "
            f"n_bootstrap={self.n_bootstrap}, n_obs={self.n_observations}, unit='{self.unit}')"
        )


class SubjectLevelBootstrap:
    """Bootstrap confidence intervals over SUBJECT-level accuracies.

    Usage:
        boot = SubjectLevelBootstrap(n_bootstrap=1000, ci_level=0.95, seed=42)
        result = boot.bootstrap(subject_accuracies)
        print(result.ci_lower, result.ci_upper)
    """

    def __init__(self, n_bootstrap: int = 1000, ci_level: float = 0.95, seed: int = 42):
        if n_bootstrap < 1:
            raise ValueError(f"n_bootstrap must be >= 1; got {n_bootstrap}")
        if not (0.0 < ci_level < 1.0):
            raise ValueError(f"ci_level must be in (0, 1); got {ci_level}")
        self.n_bootstrap = int(n_bootstrap)
        self.ci_level = float(ci_level)
        self.seed = int(seed)

    def bootstrap(self, subject_accuracies: np.ndarray) -> BootstrapResult:
        """Bootstrap the mean of `subject_accuracies` by resampling subjects
        with replacement.

        Args:
            subject_accuracies: 1D array of per-subject accuracies.

        Returns:
            BootstrapResult with mean, std, and percentile CI.
        """
        accs = np.asarray(subject_accuracies, dtype=np.float64).ravel()
        n = accs.size
        if n == 0:
            return BootstrapResult(
                mean=float("nan"), std=float("nan"),
                ci_lower=float("nan"), ci_upper=float("nan"),
                ci_level=self.ci_level, n_bootstrap=self.n_bootstrap,
                n_observations=0, unit="subject",
            )
        if n == 1:
            # Bootstrap of a single observation is degenerate; the CI is the
            # point itself. We still report it.
            val = float(accs[0])
            return BootstrapResult(
                mean=val, std=0.0,
                ci_lower=val, ci_upper=val,
                ci_level=self.ci_level, n_bootstrap=self.n_bootstrap,
                n_observations=1, unit="subject",
            )

        rng = np.random.default_rng(self.seed)
        # Resample SUBJECTS (rows), not trials. Each bootstrap iteration draws
        # `n` subjects with replacement and takes their mean accuracy.
        boot_means = np.empty(self.n_bootstrap, dtype=np.float64)
        for i in range(self.n_bootstrap):
            idx = rng.integers(0, n, size=n)
            boot_means[i] = accs[idx].mean()

        alpha = 1.0 - self.ci_level
        ci_lower = float(np.percentile(boot_means, 100.0 * (alpha / 2.0)))
        ci_upper = float(np.percentile(boot_means, 100.0 * (1.0 - alpha / 2.0)))

        return BootstrapResult(
            mean=float(accs.mean()),
            std=float(accs.std(ddof=1)) if n > 1 else 0.0,
            ci_lower=ci_lower,
            ci_upper=ci_upper,
            ci_level=self.ci_level,
            n_bootstrap=self.n_bootstrap,
            n_observations=int(n),
            unit="subject",
        )


__all__ = ["SubjectLevelBootstrap", "BootstrapResult"]
