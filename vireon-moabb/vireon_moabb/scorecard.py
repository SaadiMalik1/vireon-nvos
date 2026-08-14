"""Scorecard — 6 dimensions, 0-100 total.

Principle (ADR 0008 #9): No scorecard until underlying evidence is complete.
This scorecard raises ValueError if evidence is incomplete.
"""
from dataclasses import dataclass, field
from typing import Literal, Optional


@dataclass
class ScorecardDimension:
    name: str
    score: int
    max: int
    explanation: str


@dataclass
class Scorecard:
    dimensions: list[ScorecardDimension]
    total: int  # 0-100
    confidence: Literal["LOW", "MEDIUM", "HIGH"]


def build_scorecard(
    mean_accuracy: float,
    chance_level: float,
    chance_passed: bool,
    has_ci: bool,
    has_permutation: bool,
    permutation_significant: bool,
    n_repro_checks_passed: int,
    n_repro_checks_total: int,
    n_robustness_passed: int,
    n_robustness_total: int,
    n_data_checks_passed: int,
    n_data_checks_total: int,
    evidence_verified: bool,
) -> Scorecard:
    """Build scorecard from evidence. Raises ValueError if evidence incomplete."""
    # Principle #9: verify evidence is complete
    if not evidence_verified:
        raise ValueError(
            "Cannot generate scorecard: evidence bundle verification failed (tampered?)"
        )
    if not chance_passed:
        raise ValueError(
            "Cannot generate scorecard: accuracy at or below chance level. "
            "Fix the underlying issues before scoring."
        )

    dims = []

    # 1. Correctness (max 20)
    corr_score = 20 if chance_passed else 5
    dims.append(ScorecardDimension(
        "Correctness", corr_score, 20,
        f"Accuracy {mean_accuracy:.1%} above chance ({chance_level:.1%})"
    ))

    # 2. Statistics (max 20)
    stat_score = 0
    parts = []
    if has_ci:
        stat_score += 7
        parts.append("Subject-level CI ✓")
    if has_permutation:
        stat_score += 7
        parts.append(f"Permutation {'✓' if permutation_significant else '✗'}")
    if chance_passed:
        stat_score += 6
        parts.append("Above chance ✓")
    dims.append(ScorecardDimension("Statistics", stat_score, 20, ", ".join(parts)))

    # 3. Reproducibility (max 20)
    repro_pct = n_repro_checks_passed / n_repro_checks_total if n_repro_checks_total > 0 else 0
    repro_score = int(20 * repro_pct)
    dims.append(ScorecardDimension(
        "Reproducibility", repro_score, 20,
        f"{n_repro_checks_passed}/{n_repro_checks_total} checks passed"
    ))

    # 4. Robustness (max 20)
    if n_robustness_total > 0:
        rob_score = int(20 * n_robustness_passed / n_robustness_total)
        dims.append(ScorecardDimension(
            "Robustness", rob_score, 20,
            f"{n_robustness_passed}/{n_robustness_total} perturbations passed"
        ))
    else:
        dims.append(ScorecardDimension("Robustness", 0, 20, "No robustness testing"))

    # 5. Data Quality (max 20)
    dq_pct = n_data_checks_passed / n_data_checks_total if n_data_checks_total > 0 else 0
    dq_score = int(20 * dq_pct)
    dims.append(ScorecardDimension(
        "Data Quality", dq_score, 20,
        f"{n_data_checks_passed}/{n_data_checks_total} checks passed"
    ))

    # 6. Evidence Integrity (max 20)
    evi_score = 20 if evidence_verified else 0
    dims.append(ScorecardDimension(
        "Evidence Integrity", evi_score, 20,
        "Evidence hash verified ✓" if evidence_verified else "Evidence hash MISMATCH"
    ))

    total = sum(d.score for d in dims) * 100 // 120
    confidence = "HIGH" if total >= 80 else ("MEDIUM" if total >= 60 else "LOW")

    return Scorecard(dimensions=dims, total=total, confidence=confidence)
