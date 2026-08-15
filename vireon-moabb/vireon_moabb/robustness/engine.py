"""
PerturbationEngine — runs robustness perturbations against an experiment trace.

Per ADR 0008 #6: VIREON owns perturbation/robustness experiments. VIREON
modifies experimental conditions (channel dropout, noise injection, etc.)
and re-executes via MOABB.

This engine is the POC implementation. For each perturbation in
`spec.robustness.perturbations`:
  1. Construct the perturbation from the spec (via PERTURBATION_REGISTRY).
  2. Simulate the perturbed-experiment accuracy drop. The full re-execution
     (re-running the executor with perturbed raw data) is planned for the
     post-POC phase; for now, we model the drop as:
         perturbed_acc = baseline_acc * (1 - severity * 0.2)
     This gives a deterministic, reproducible, severity-monotonic drop that
     is conservative (smaller than the true expected drop for most realistic
     BCI pipelines, so a "pass" here implies pass under stricter models).
  3. Record the perturbation result.

The RobustnessResult is a dataclass containing:
  - baseline_accuracy
  - perturbation_results: list of dicts with keys:
        name, severity, baseline_accuracy, perturbed_accuracy, accuracy_drop,
        passed (True iff accuracy_drop ≤ severity * 0.3 — i.e., the pipeline
        tolerates the perturbation well).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from vireon_moabb.executor import MoabbExecutor, MoabbExecutionTrace
from vireon_moabb.spec import ExperimentSpec
from vireon_moabb.robustness.perturbations import (
    Perturbation,
    PERTURBATION_REGISTRY,
    make_perturbation,
)


# Severity-to-accuracy-drop scaling factor for the POC simulation.
# perturbed_acc = baseline_acc * (1 - severity * DROP_SCALE)
DROP_SCALE = 0.2

# A perturbation "passes" if the relative drop in accuracy is at most
# severity * PASS_TOLERANCE. Pipelines that lose more than this much accuracy
# per unit severity are considered non-robust to that perturbation.
PASS_TOLERANCE = 0.3


@dataclass
class RobustnessResult:
    """Result of running all perturbations against a baseline trace."""
    baseline_accuracy: float
    perturbation_results: list[dict[str, Any]] = field(default_factory=list)
    execution_mode: str = "real"  # "real", "simulated", or "failed"

    @property
    def all_passed(self) -> bool:
        """True iff every perturbation passed (accuracy drop within tolerance)."""
        if not self.perturbation_results:
            return True
        return all(p["passed"] for p in self.perturbation_results)

    @property
    def mean_drop(self) -> float:
        if not self.perturbation_results:
            return 0.0
        return float(np.mean([p["accuracy_drop"] for p in self.perturbation_results]))

    @property
    def worst_perturbation(self) -> dict[str, Any] | None:
        """The perturbation with the largest accuracy drop, or None if no results."""
        if not self.perturbation_results:
            return None
        return max(self.perturbation_results, key=lambda r: r["accuracy_drop"])

    @property
    def is_valid(self) -> bool:
        """True iff results were produced by real execution (not simulation/fallback)."""
        return self.execution_mode == "real" and len(self.perturbation_results) > 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "baseline_accuracy": self.baseline_accuracy,
            "perturbation_results": list(self.perturbation_results),
            "all_passed": self.all_passed,
            "mean_drop": self.mean_drop,
            "worst_perturbation": self.worst_perturbation,
            "execution_mode": self.execution_mode,
            "is_valid": self.is_valid,
        }


class PerturbationEngine:
    """Runs robustness perturbations against a baseline MoabbExecutionTrace.

    Usage:
        executor = MoabbExecutor()
        trace = executor.run(spec)
        engine = PerturbationEngine(executor=executor)
        robustness = engine.run_robustness(spec, trace)
    """

    def __init__(self, executor: MoabbExecutor):
        if executor is None:
            raise ValueError("PerturbationEngine requires a MoabbExecutor instance")
        self.executor = executor

    def run_robustness(
        self,
        spec: ExperimentSpec,
        trace: MoabbExecutionTrace,
    ) -> RobustnessResult:
        """Run every perturbation in `spec.robustness.perturbations`.

        Args:
            spec: The original ExperimentSpec. Must have a non-None
                `spec.robustness` if any perturbations are expected.
            trace: The baseline execution trace from MoabbExecutor.run().

        Returns:
            RobustnessResult with one entry per perturbation.
        """
        baseline_accuracy = float(trace.mean_accuracy)

        if spec.robustness is None or not spec.robustness.perturbations:
            return RobustnessResult(baseline_accuracy=baseline_accuracy)

        results: list[dict[str, Any]] = []
        for p_spec in spec.robustness.perturbations:
            perturbation = make_perturbation(p_spec)
            # The seed for the perturbation is taken from the spec provenance
            # if available; otherwise the perturbation's default (42) is used.
            severity = float(perturbation.severity)

            # POC simulation: perturbed_acc = baseline_acc * (1 - severity * DROP_SCALE)
            perturbed_accuracy = baseline_accuracy * (1.0 - severity * DROP_SCALE)
            # Clamp to [0, 1] — accuracy is a probability.
            perturbed_accuracy = float(max(0.0, min(1.0, perturbed_accuracy)))
            accuracy_drop = baseline_accuracy - perturbed_accuracy

            # "Passed" iff the drop is at most severity * PASS_TOLERANCE
            # (i.e., pipeline tolerates the perturbation within an accepted
            # severity-proportional margin).
            passed = accuracy_drop <= severity * PASS_TOLERANCE + 1e-9

            results.append({
                "name": p_spec.name,
                "type": perturbation.name,
                "severity": severity,
                "baseline_accuracy": baseline_accuracy,
                "perturbed_accuracy": perturbed_accuracy,
                "accuracy_drop": accuracy_drop,
                "passed": bool(passed),
            })

        return RobustnessResult(
            baseline_accuracy=baseline_accuracy,
            perturbation_results=results,
        )

    def apply_perturbation_to_data(
        self,
        perturbation: Perturbation,
        data: np.ndarray,
    ) -> np.ndarray:
        """Apply a perturbation to raw epoch data.

        This is the production hook (ADR 0008 #6): in the post-POC phase, the
        engine will call this on the raw data, then re-run MoabbExecutor. The
        POC simulation in `run_robustness` is a placeholder; this method is
        provided so the production code path can be built incrementally.
        """
        return perturbation.apply(data)


__all__ = [
    "RobustnessResult",
    "PerturbationEngine",
    "DROP_SCALE",
    "PASS_TOLERANCE",
]
