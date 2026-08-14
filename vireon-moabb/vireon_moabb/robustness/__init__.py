"""
VIREON × MOABB — Robustness layer.

Per ADR 0008 #6: VIREON owns perturbation/robustness experiments. VIREON
modifies experimental conditions (channel dropout, noise injection) and
re-executes via MOABB. VIREON does not perturb results post-hoc.

This subpackage provides:
  - 5 perturbation classes (ChannelDropout, WhiteNoise, LineNoise, TimeShift,
    AmplitudeScaling) — each reproducible (seeded) and severity-controlled.
  - A PERTURBATION_REGISTRY mapping type strings to classes.
  - A PerturbationEngine that runs each perturbation against a baseline trace
    and returns a RobustnessResult.

The current engine uses a POC simulation for the accuracy drop (deterministic,
severity-monotonic). The `apply_perturbation_to_data` hook on the engine is
the production entry point for true re-execution via MOABB.
"""
from vireon_moabb.robustness.perturbations import (
    Perturbation,
    ChannelDropout,
    WhiteNoise,
    LineNoise,
    TimeShift,
    AmplitudeScaling,
    PERTURBATION_REGISTRY,
    make_perturbation,
)
from vireon_moabb.robustness.engine import (
    RobustnessResult,
    PerturbationEngine,
)

__all__ = [
    "Perturbation",
    "ChannelDropout",
    "WhiteNoise",
    "LineNoise",
    "TimeShift",
    "AmplitudeScaling",
    "PERTURBATION_REGISTRY",
    "make_perturbation",
    "RobustnessResult",
    "PerturbationEngine",
]
