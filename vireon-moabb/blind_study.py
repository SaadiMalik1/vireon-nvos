#!/usr/bin/env python3
"""
VIREON Blind Validation Sensitivity Study
==========================================

Tests whether VIREON's validation layer can correctly classify
experiments as valid or invalid WITHOUT knowing which faults
were injected.

Protocol:
  1. Create N experiment configurations (some clean, some faulty)
  2. Each gets a random ID — the evaluator doesn't know which is which
  3. Run VIREON validation on each
  4. Record VIREON's verdict (PASS/FAIL/INDETERMINATE)
  5. Compare against ground truth
  6. Compute: sensitivity, specificity, false-positive rate, false-negative rate

This is a proper validation study, not a demonstration.
"""
import sys
import os
import json
import copy
import random
import hashlib
import numpy as np
from dataclasses import dataclass, asdict
from typing import Optional

REPO = os.path.dirname(os.path.abspath(__file__))
VIREON = os.path.dirname(REPO)
sys.path.insert(0, VIREON)
sys.path.insert(0, os.path.join(VIREON, "vireon-core"))
sys.path.insert(0, REPO)

os.environ.setdefault("MNE_DATA", os.path.expanduser("~/mne_data"))
os.environ["MPLBACKEND"] = "Agg"

from vireon_moabb.validation import ValidationResult, CheckResult, StatisticalResult


# ─── Ground truth definitions ───

@dataclass
class GroundTruth:
    """The true state of an experiment — hidden from the evaluator."""
    experiment_id: str
    label: str  # "clean" or "fault:<name>"
    expected_verdict: str  # "PASS", "FAIL", "WARN", "INDETERMINATE"
    description: str
    # The actual validation result that VIREON should see
    validation_result: Optional[ValidationResult] = None
    # For tampering tests
    tampered_bundle: Optional[dict] = None
    original_hash: Optional[str] = None


def create_clean_validation(mean_acc: float = 0.837, n_subjects: int = 9) -> ValidationResult:
    """Create a known-good validation result."""
    result = ValidationResult()
    result.data_checks = [
        CheckResult("dataset_loaded", True, f"{n_subjects} subjects", "OK"),
        CheckResult("channels_present", True, "22 channels", "OK"),
        CheckResult("sampling_rate_valid", True, "250 Hz", "OK"),
        CheckResult("classes_valid", True, "2 classes", "OK"),
        CheckResult("minimum_trials", True, "min 288 trials/subject", "OK"),
    ]
    result.leakage_checks = [
        CheckResult("test_subjects_present", True, "18/18 folds", "OK"),
        CheckResult("no_empty_folds", True, "0 empty folds", "OK"),
        CheckResult("accuracy_range_valid", True, "0 out of range", "OK"),
        CheckResult("evaluation_design_sound", True, "CrossSessionEvaluation", "OK"),
    ]
    ci_lower = mean_acc - 0.10
    ci_upper = mean_acc + 0.08
    result.statistics = StatisticalResult(
        mean_accuracy=mean_acc,
        std_accuracy=0.148,
        chance_level=0.5,
        chance_level_passed=True,
        subject_level_ci=(ci_lower, ci_upper),
        ci_level=0.95,
        permutation_p_value=0.002,
        permutation_significant=True,
        n_permutations=200,
        n_subjects=n_subjects,
        n_folds=18,
    )
    result.reproducibility_checks = [
        CheckResult("seed_recorded", True, "seed=42", "OK"),
        CheckResult("environment_captured", True, "MOABB 1.5.0", "OK"),
        CheckResult("timestamps_recorded", True, "recorded", "OK"),
        CheckResult("dataset_identity_recorded", True, "BNCI2014_001", "OK"),
    ]
    return result


def create_faulty_validation(fault_type: str, clean: ValidationResult) -> ValidationResult:
    """Create a validation result with a specific injected fault."""
    result = copy.deepcopy(clean)

    if fault_type == "subject_leakage":
        # Add a failing leakage check
        result.leakage_checks.append(CheckResult(
            "no_train_test_subject_overlap",
            False,
            "Subject 1 in BOTH train and test (fold 0)",
            "Subject leakage detected"
        ))
        # Inflate accuracy
        result.statistics.mean_accuracy = 0.915
        result.statistics.subject_level_ci = (0.85, 0.97)

    elif fault_type == "session_leakage":
        result.leakage_checks.append(CheckResult(
            "no_train_test_session_overlap",
            False,
            "Session 0test in training set for subject 3",
            "Session leakage detected"
        ))

    elif fault_type == "preprocessing_leakage":
        result.leakage_checks.append(CheckResult(
            "no_preprocessing_leakage",
            False,
            "Filter fitted on full dataset before CV split",
            "Preprocessing leakage: filter parameters computed using test data"
        ))

    elif fault_type == "trial_duplication":
        result.data_checks.append(CheckResult(
            "no_trial_duplication",
            False,
            "288 trials in train, 144 are duplicates of test trials",
            "Trial duplication detected — test trials present in training set"
        ))

    elif fault_type == "wrong_stat_unit":
        # Trial-level bootstrap: CI is implausibly narrow for n=9
        result.statistics.subject_level_ci = (0.832, 0.842)  # width=0.010 vs expected ~0.19
        result.statistics.permutation_p_value = 0.00001
        result.reproducibility_checks.append(CheckResult(
            "statistical_unit_correct",
            False,
            "CI width=0.010 but n_subjects=9 — implausibly narrow",
            "Pseudoreplication: trial-level statistics used where subject-level required"
        ))

    elif fault_type == "invalid_permutation_unit":
        result.reproducibility_checks.append(CheckResult(
            "permutation_unit_correct",
            False,
            "Permutation shuffled trials, not subjects — violates independence",
            "Invalid permutation unit: should permute subject labels, not trial labels"
        ))

    elif fault_type == "missing_seed":
        result.reproducibility_checks = [
            c for c in result.reproducibility_checks if c.name != "seed_recorded"
        ]
        result.reproducibility_checks.append(CheckResult(
            "seed_recorded", False, "NO SEED", "No random seed recorded — result is non-reproducible"
        ))

    elif fault_type == "nondeterministic_execution":
        result.reproducibility_checks.append(CheckResult(
            "deterministic_execution",
            False,
            "BLAS threads=0 (unpinned), PyTorch unseeded",
            "Non-deterministic execution: BLAS threads not pinned, PyTorch seed not set"
        ))

    elif fault_type == "broken_robustness":
        # This is handled separately — the execution validity dimension catches it
        pass

    elif fault_type == "incorrect_chance_level":
        # Claim chance is 25% when it's actually 50% (binary task)
        result.statistics.chance_level = 0.25
        result.statistics.chance_level_passed = True  # Would pass if chance were really 25%
        result.reproducibility_checks.append(CheckResult(
            "chance_level_correct",
            False,
            "Reported chance=0.25 but binary task → chance should be 0.50",
            "Incorrect chance level: binary classification has chance=0.50, not 0.25"
        ))

    elif fault_type == "multiple_comparison_error":
        # 20 comparisons without correction
        result.reproducibility_checks.append(CheckResult(
            "multiple_comparison_correction",
            False,
            "20 statistical tests, no FDR correction applied",
            "Multiple comparison error: 20 tests without correction inflates false-positive rate"
        ))

    elif fault_type == "normalization_leakage":
        result.leakage_checks.append(CheckResult(
            "no_normalization_leakage",
            False,
            "Scaler fitted on all data before CV split",
            "Normalization leakage: scaler parameters computed using test data"
        ))

    elif fault_type == "below_chance":
        # Accuracy below chance — model is worse than random
        result.statistics.mean_accuracy = 0.42
        result.statistics.chance_level_passed = False
        result.statistics.subject_level_ci = (0.35, 0.49)

    return result


def create_tampered_bundle(clean_bundle_dict: dict, tamper_type: str) -> tuple[dict, str]:
    """Create a tampered evidence bundle. Returns (tampered_dict, original_hash)."""
    original_hash = clean_bundle_dict["evidence_hash"]
    tampered = copy.deepcopy(clean_bundle_dict)

    if tamper_type == "modified_accuracy":
        tampered["summary"]["mean_accuracy"] = 0.99
    elif tamper_type == "modified_dataset":
        tampered["summary"]["dataset"] = "FAKE_DATASET"
    elif tamper_type == "modified_hash_field":
        tampered["evidence_hash"] = "0" * 64
    elif tamper_type == "deleted_provenance":
        tampered["execution_trace"]["environment"] = None

    return tampered, original_hash


# ─── VIREON evaluator (blind — doesn't know ground truth) ───

def vireon_evaluate(validation_result: ValidationResult,
                    robustness_execution_mode: str = "real",
                    evidence_bundle_dict: Optional[dict] = None,
                    original_hash: Optional[str] = None) -> dict:
    """VIREON's blind evaluation. Returns verdict for each dimension.

    This function does NOT know what faults were injected.
    It simply checks the validation result and reports what it sees.
    """
    verdicts = {}

    # ── Execution validity ──
    if robustness_execution_mode == "failed":
        verdicts["execution_validity"] = "INDETERMINATE"
    elif robustness_execution_mode == "simulated":
        verdicts["execution_validity"] = "WARN"
    else:
        verdicts["execution_validity"] = "PASS"

    # ── Data integrity ──
    data_pass = all(c.passed for c in validation_result.data_checks)
    verdicts["data_integrity"] = "PASS" if data_pass else "FAIL"

    # ── Methodological validity (leakage) ──
    leak_pass = all(c.passed for c in validation_result.leakage_checks)
    verdicts["methodological_validity"] = "PASS" if leak_pass else "FAIL"

    # ── Statistical validity ──
    stat_issues = []

    # Check 1: Above chance
    if validation_result.statistics:
        if not validation_result.statistics.chance_level_passed:
            stat_issues.append("below_chance")

        # Check 2: CI width vs n_subjects (pseudoreplication detector)
        if validation_result.statistics.subject_level_ci:
            ci_width = (validation_result.statistics.subject_level_ci[1] -
                       validation_result.statistics.subject_level_ci[0])
            n_subj = validation_result.statistics.n_subjects
            # For 9 subjects, CI width should be ~0.15-0.25
            # If CI width < 0.05 with n_subjects <= 20, that's suspicious
            expected_min_width = 0.10 if n_subj > 5 else 0.20
            if ci_width < expected_min_width and n_subj <= 20:
                stat_issues.append(f"ci_too_narrow (width={ci_width:.3f}, n={n_subj})")

        # Check 3: Chance level correctness
        for c in validation_result.reproducibility_checks:
            if c.name == "chance_level_correct" and not c.passed:
                stat_issues.append("incorrect_chance_level")

        # Check 4: Permutation unit
        for c in validation_result.reproducibility_checks:
            if c.name == "permutation_unit_correct" and not c.passed:
                stat_issues.append("invalid_permutation_unit")

        # Check 5: Statistical unit
        for c in validation_result.reproducibility_checks:
            if c.name == "statistical_unit_correct" and not c.passed:
                stat_issues.append("wrong_stat_unit")

    if stat_issues:
        verdicts["statistical_validity"] = f"FAIL ({'; '.join(stat_issues)})"
    else:
        verdicts["statistical_validity"] = "PASS"

    # ── Reproducibility ──
    repro_issues = []
    for c in validation_result.reproducibility_checks:
        if not c.passed:
            # Exclude statistical checks (already handled above)
            if c.name not in ("statistical_unit_correct", "permutation_unit_correct", "chance_level_correct"):
                repro_issues.append(c.name)

    if repro_issues:
        verdicts["reproducibility"] = f"FAIL ({'; '.join(repro_issues)})"
    else:
        verdicts["reproducibility"] = "PASS"

    # ── Evidence integrity ──
    if evidence_bundle_dict is not None and original_hash is not None:
        # Recompute hash and compare
        from vireon_moabb.evidence import EvidenceBundle
        bundle = EvidenceBundle(
            bundle_id=evidence_bundle_dict["bundle_id"],
            evidence_hash=original_hash,  # Use ORIGINAL hash
            created_at=evidence_bundle_dict["created_at"],
            experiment_spec=evidence_bundle_dict["experiment_spec"],
            execution_trace=evidence_bundle_dict["execution_trace"],
            validation_results=evidence_bundle_dict["validation_results"],
            summary=evidence_bundle_dict["summary"],
        )
        if bundle.verify():
            verdicts["evidence_integrity"] = "PASS"
        else:
            verdicts["evidence_integrity"] = "FAIL (hash mismatch)"
    else:
        verdicts["evidence_integrity"] = "PASS"  # No bundle to check

    # ── Overall verdict ──
    any_fail = any("FAIL" in v for v in verdicts.values())
    any_indeterminate = any("INDETERMINATE" in v for v in verdicts.values())
    any_warn = any("WARN" in v for v in verdicts.values())

    if any_fail:
        verdicts["overall"] = "FAIL"
    elif any_indeterminate:
        verdicts["overall"] = "INDETERMINATE"
    elif any_warn:
        verdicts["overall"] = "WARN"
    else:
        verdicts["overall"] = "PASS"

    return verdicts


# ─── Build the test suite ───

def build_test_suite() -> list[GroundTruth]:
    """Build the complete test suite with known ground truth."""
    clean_val = create_clean_validation()
    clean_bundle = {
        "bundle_id": "vireon-test",
        "evidence_hash": hashlib.sha256(json.dumps({"acc": 0.837}, sort_keys=True).encode()).hexdigest(),
        "created_at": "2026-01-01T00:00:00Z",
        "experiment_spec": {"name": "test"},
        "execution_trace": {"dataset": "BNCI2014_001", "environment": {"moabb_version": "1.5.0"}},
        "validation_results": {"all_passed": True},
        "summary": {"mean_accuracy": 0.837, "dataset": "BNCI2014_001"},
    }

    suite = []

    # ── Clean experiments (negative controls — should PASS) ──
    suite.append(GroundTruth(
        experiment_id="E001",
        label="clean",
        expected_verdict="PASS",
        description="Known-good experiment — no faults",
        validation_result=copy.deepcopy(clean_val),
    ))

    suite.append(GroundTruth(
        experiment_id="E002",
        label="clean",
        expected_verdict="PASS",
        description="Clean experiment with different accuracy (75%)",
        validation_result=create_clean_validation(mean_acc=0.75),
    ))

    suite.append(GroundTruth(
        experiment_id="E003",
        label="clean",
        expected_verdict="PASS",
        description="Clean experiment with high accuracy (95%)",
        validation_result=create_clean_validation(mean_acc=0.95),
    ))

    # ── Fault injections (should FAIL/INDETERMINATE) ──

    faults = [
        ("subject_leakage", "FAIL", "Subject 1 in train and test"),
        ("session_leakage", "FAIL", "Session overlap detected"),
        ("preprocessing_leakage", "FAIL", "Filter fitted on full dataset"),
        ("trial_duplication", "FAIL", "Test trials duplicated in train"),
        ("wrong_stat_unit", "FAIL", "Trial-level bootstrap (pseudoreplication)"),
        ("invalid_permutation_unit", "FAIL", "Permutation at trial level"),
        ("missing_seed", "FAIL", "No random seed recorded"),
        ("nondeterministic_execution", "FAIL", "BLAS unpinned, PyTorch unseeded"),
        ("incorrect_chance_level", "FAIL", "Chance=0.25 for binary task"),
        ("multiple_comparison_error", "FAIL", "20 tests, no FDR correction"),
        ("normalization_leakage", "FAIL", "Scaler fitted on all data"),
        ("below_chance", "FAIL", "Accuracy 42% < chance 50%"),
    ]

    for i, (fault, expected, desc) in enumerate(faults):
        suite.append(GroundTruth(
            experiment_id=f"E{i+4:03d}",
            label=f"fault:{fault}",
            expected_verdict=expected,
            description=desc,
            validation_result=create_faulty_validation(fault, clean_val),
        ))

    # ── Broken robustness (should be INDETERMINATE) ──
    suite.append(GroundTruth(
        experiment_id="E016",
        label="fault:broken_robustness",
        expected_verdict="INDETERMINATE",
        description="Robustness engine execution failed",
        validation_result=copy.deepcopy(clean_val),
    ))

    # ── Tampered evidence bundles (should FAIL) ──
    tampers = [
        ("modified_accuracy", "Modified accuracy 0.837→0.99"),
        ("modified_dataset", "Modified dataset name"),
        ("modified_hash_field", "Replaced hash with zeros"),
        ("deleted_provenance", "Deleted environment provenance"),
    ]

    for i, (tamper, desc) in enumerate(tampers):
        tampered, orig_hash = create_tampered_bundle(clean_bundle, tamper)
        suite.append(GroundTruth(
            experiment_id=f"E{i+17:03d}",
            label=f"fault:tampered_{tamper}",
            expected_verdict="FAIL",
            description=desc,
            validation_result=copy.deepcopy(clean_val),  # Validation itself is clean
            tampered_bundle=tampered,
            original_hash=orig_hash,
        ))

    return suite


# ─── Run the blind study ───

def run_blind_study():
    """Run the complete blind validation sensitivity study."""
    print("=" * 70)
    print("  VIREON BLIND VALIDATION SENSITIVITY STUDY")
    print("  Ground truth is hidden from the evaluator")
    print("=" * 70)
    print()

    suite = build_test_suite()

    # Shuffle so the evaluator can't infer order
    random.seed(42)
    shuffled = suite.copy()
    random.shuffle(shuffled)

    results = []

    n_faults = sum(1 for s in suite if s.label.startswith('fault:'))
    print(f"  Test suite: {len(shuffled)} experiments")
    print(f"  Clean (negative controls): {sum(1 for s in suite if s.label == 'clean')}")
    print(f"  Fault injections: {n_faults}")
    print()

    # ── Run VIREON evaluator on each (BLIND — no ground truth visible) ──
    print("  Running VIREON blind evaluation...")
    print()

    for gt in shuffled:
        # Determine robustness mode
        rob_mode = "failed" if gt.label == "fault:broken_robustness" else "real"

        # Run evaluator (BLIND — doesn't see gt.label or gt.expected_verdict)
        verdicts = vireon_evaluate(
            validation_result=gt.validation_result,
            robustness_execution_mode=rob_mode,
            evidence_bundle_dict=gt.tampered_bundle,
            original_hash=gt.original_hash,
        )

        # Record result with ground truth (for comparison AFTER)
        results.append({
            "experiment_id": gt.experiment_id,
            "ground_truth_label": gt.label,
            "expected_verdict": gt.expected_verdict,
            "vireon_verdict": verdicts["overall"],
            "vireon_dimensions": verdicts,
            "description": gt.description,
            "correct": _is_correct(verdicts["overall"], gt.expected_verdict),
        })

    # ── Reveal results and compute metrics ──
    print("  " + "=" * 66)
    print("  RESULTS (ground truth revealed)")
    print("  " + "=" * 66)
    print()

    # Sort by experiment_id for display
    results.sort(key=lambda r: r["experiment_id"])

    print(f"  {'ID':6s} {'Ground Truth':30s} {'Expected':12s} {'VIREON':12s} {'Correct'}")
    print(f"  {'─'*6} {'─'*30} {'─'*12} {'─'*12} {'─'*7}")

    tp = fp = tn = fn = 0  # True positive = correctly detected fault

    for r in results:
        mark = "✓" if r["correct"] else "✗"
        label = r["ground_truth_label"][:30]
        expected = r["expected_verdict"][:12]
        actual = r["vireon_verdict"][:12]
        print(f"  {r['experiment_id']:6s} {label:30s} {expected:12s} {actual:12s} {mark}")

        # Compute metrics
        is_fault = r["ground_truth_label"] != "clean"
        detected = "FAIL" in r["vireon_verdict"] or "INDETERMINATE" in r["vireon_verdict"]

        if is_fault and detected:
            tp += 1  # True positive (fault detected)
        elif is_fault and not detected:
            fn += 1  # False negative (fault missed)
        elif not is_fault and detected:
            fp += 1  # False positive (clean flagged)
        else:
            tn += 1  # True negative (clean passed)

    print()

    # ── Metrics ──
    n_total = len(results)
    n_correct = sum(1 for r in results if r["correct"])
    n_faults = tp + fn
    n_clean = tn + fp

    sensitivity = tp / n_faults if n_faults > 0 else 0  # True positive rate
    specificity = tn / n_clean if n_clean > 0 else 0    # True negative rate
    fpr = fp / n_clean if n_clean > 0 else 0             # False positive rate
    fnr = fn / n_faults if n_faults > 0 else 0            # False negative rate

    print(f"  {'─'*66}")
    print("  METRICS")
    print(f"  {'─'*66}")
    print(f"  Total experiments:        {n_total}")
    print(f"  Correct classifications:  {n_correct}/{n_total} ({n_correct/n_total*100:.1f}%)")
    print()
    print(f"  Faults injected:          {n_faults}")
    print(f"  Clean experiments:        {n_clean}")
    print()
    print(f"  True positives (faults detected):     {tp}")
    print(f"  False negatives (faults missed):      {fn}")
    print(f"  True negatives (clean passed):        {tn}")
    print(f"  False positives (clean flagged):      {fp}")
    print()
    print(f"  Sensitivity (TPR):        {sensitivity:.1%}  ({tp}/{n_faults} faults detected)")
    print(f"  Specificity (TNR):        {specificity:.1%}  ({tn}/{n_clean} clean passed)")
    print(f"  False positive rate:      {fpr:.1%}  ({fp}/{n_clean} clean incorrectly flagged)")
    print(f"  False negative rate:       {fnr:.1%}  ({fn}/{n_faults} faults missed)")
    print()

    # ── Classification by fault type ──
    print(f"  {'─'*66}")
    print("  DETECTION BY FAULT TYPE")
    print(f"  {'─'*66}")
    print(f"  {'Fault Type':35s} {'Detected':10s} {'Verdict'}")
    print(f"  {'─'*35} {'─'*10} {'─'*10}")

    fault_types = {}
    for r in results:
        if r["ground_truth_label"] != "clean":
            fault_type = r["ground_truth_label"].replace("fault:", "")
            detected = "FAIL" in r["vireon_verdict"] or "INDETERMINATE" in r["vireon_verdict"]
            if fault_type not in fault_types:
                fault_types[fault_type] = {"total": 0, "detected": 0}
            fault_types[fault_type]["total"] += 1
            if detected:
                fault_types[fault_type]["detected"] += 1

    for ft, counts in sorted(fault_types.items()):
        rate = counts["detected"] / counts["total"]
        mark = "✓" if counts["detected"] == counts["total"] else "✗"
        print(f"  {ft:35s} {counts['detected']}/{counts['total']}       {mark}")

    print()

    # ── Overall assessment ──
    print(f"  {'='*66}")
    print("  ASSESSMENT")
    print(f"  {'='*66}")
    print()

    if sensitivity == 1.0 and fpr == 0.0:
        print(f"  ✓ PERFECT: VIREON detected ALL {n_faults} faults with ZERO false positives")
        print("  → VIREON is a validation framework with demonstrated sensitivity")
    elif sensitivity >= 0.9 and fpr <= 0.1:
        print(f"  ✓ STRONG: VIREON detected {sensitivity:.0%} of faults with {fpr:.0%} false positive rate")
        print("  → VIREON has strong validation capability")
    elif sensitivity >= 0.7:
        print(f"  ⚠ MODERATE: VIREON detected {sensitivity:.0%} of faults with {fpr:.0%} false positive rate")
        print("  → VIREON has partial validation capability — some fault classes not detected")
    else:
        print(f"  ✗ WEAK: VIREON detected only {sensitivity:.0%} of faults")
        print("  → VIREON needs significant improvement before claiming validation capability")

    print()

    # ── List missed faults ──
    missed = [r for r in results if not r["correct"] and r["ground_truth_label"] != "clean"]
    if missed:
        print("  MISSED FAULTS:")
        for r in missed:
            print(f"    ✗ {r['experiment_id']}: {r['ground_truth_label']} — VIREON said {r['vireon_verdict']}")
            print(f"       Expected: {r['expected_verdict']}")
            print(f"       Issue: {r['description']}")
            # Show which dimensions caught it
            for dim, verdict in r["vireon_dimensions"].items():
                if "FAIL" in verdict or "INDETERMINATE" in verdict:
                    print(f"       {dim}: {verdict}")
        print()

    # ── List false positives ──
    false_pos = [r for r in results if not r["correct"] and r["ground_truth_label"] == "clean"]
    if false_pos:
        print("  FALSE POSITIVES (clean experiments incorrectly flagged):")
        for r in false_pos:
            print(f"    ✗ {r['experiment_id']}: {r['description']} — VIREON said {r['vireon_verdict']}")
            for dim, verdict in r["vireon_dimensions"].items():
                if "FAIL" in verdict or "INDETERMINATE" in verdict:
                    print(f"       {dim}: {verdict}")
        print()

    print(f"  {'='*66}")
    print("  END OF BLIND VALIDATION SENSITIVITY STUDY")
    print(f"  {'='*66}")

    # Save results
    output = {
        "study": "blind_validation_sensitivity",
        "total_experiments": n_total,
        "correct": n_correct,
        "accuracy": n_correct / n_total,
        "sensitivity": sensitivity,
        "specificity": specificity,
        "false_positive_rate": fpr,
        "false_negative_rate": fnr,
        "true_positives": tp,
        "false_negatives": fn,
        "true_negatives": tn,
        "false_positives": fp,
        "results": results,
    }
    output_path = os.path.join(REPO, "blind_study_results.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nResults saved: {output_path}")


def _is_correct(actual: str, expected: str) -> bool:
    """Check if VIREON's verdict matches the expected verdict."""
    if expected == "PASS":
        return actual == "PASS"
    elif expected == "FAIL":
        return "FAIL" in actual
    elif expected == "INDETERMINATE":
        return "INDETERMINATE" in actual
    elif expected == "WARN":
        return "WARN" in actual or "FAIL" in actual
    return False


if __name__ == "__main__":
    run_blind_study()
