#!/usr/bin/env python3
"""
VIREON Study B — End-to-End Fault Detection
=============================================

Tests whether VIREON's ACTUAL ValidationLayer can detect faults
injected into the RAW EXECUTION TRACE — NOT into pre-built
ValidationResult objects.

This is the honest test. The fault is in the DATA, not in the verdict.

Faults are injected into the MoabbExecutionTrace (the raw output of
MoabbExecutor.run()). VIREON's ValidationLayer.validate() then runs
on the contaminated trace and must DISCOVER the fault independently.

Key difference from Study A:
  Study A: fault injected into ValidationResult → evaluator reads it → PASS/FAIL
  Study B: fault injected into execution trace → ValidationLayer runs → discovery?
"""
import sys
import os
import json
import copy
import numpy as np
from dataclasses import dataclass, asdict
from typing import Optional

REPO = os.path.dirname(os.path.abspath(__file__))
VIREON = os.path.dirname(REPO)
sys.path.insert(0, VIREON)
sys.path.insert(0, os.path.join(VIREON, "vireon-core"))
sys.path.insert(0, REPO)

os.environ["MPLBACKEND"] = "Agg"

from vireon_moabb.validation import ValidationLayer, CheckResult
from vireon_moabb.executor import MoabbExecutionTrace, DatasetMetadata, FoldResult, EvaluationPartition, EnvironmentFingerprint
from vireon_moabb.spec import ExperimentSpec, StatisticsSpec, ProvenanceSpec
from vireon_moabb.evidence import EvidenceAssembler


def load_cached_trace() -> tuple[dict, ExperimentSpec]:
    """Load the cached experiment1 trace and spec."""
    with open(os.path.join(REPO, "experiment1_evidence_bundle.json")) as f:
        bundle = json.load(f)
    
    # Reconstruct spec
    spec = ExperimentSpec(**bundle["experiment_spec"])
    return bundle, spec


def reconstruct_trace(bundle_dict: dict) -> MoabbExecutionTrace:
    """Reconstruct a MoabbExecutionTrace from the bundle dict."""
    trace_dict = bundle_dict["execution_trace"]
    
    # Reconstruct dataset metadata
    dm = DatasetMetadata(**trace_dict["dataset_metadata"])
    
    # Reconstruct partitions
    partitions = [EvaluationPartition(**p) for p in trace_dict["partitions"]]
    
    # Reconstruct fold results
    fold_results = [FoldResult(**r) for r in trace_dict["fold_results"]]
    
    # Reconstruct environment
    env = EnvironmentFingerprint(**trace_dict["environment"])
    
    return MoabbExecutionTrace(
        spec=trace_dict["spec"],
        dataset_metadata=dm,
        partitions=partitions,
        fold_results=fold_results,
        environment=env,
        seed=trace_dict["seed"],
        execution_started_at=trace_dict["execution_started_at"],
        execution_finished_at=trace_dict["execution_finished_at"],
    )


# ─── Fault injection into RAW EXECUTION TRACE ───

def inject_subject_leakage_into_trace(trace: MoabbExecutionTrace) -> MoabbExecutionTrace:
    """Inject subject+session leakage for CrossSessionEvaluation.
    
    For CrossSessionEvaluation, same subject in train and test is VALID
    if they're from different sessions. The fault is: same subject AND
    same session in both train and test — this is true contamination.
    
    We inject: subject 1, session S (the test session) into the training set.
    """
    contaminated = copy.deepcopy(trace)
    
    # Get the test session of fold 0
    test_session = contaminated.partitions[0].test_sessions[0] if contaminated.partitions[0].test_sessions else 1
    test_subject = contaminated.partitions[0].test_subjects[0] if contaminated.partitions[0].test_subjects else 1
    
    # Inject: same subject AND same session into training set
    contaminated.partitions[0].train_subjects = [test_subject]  # Same subject in train
    contaminated.partitions[0].train_sessions = [test_session]  # SAME session — this is the leakage
    
    # The accuracy for this fold will be inflated (we simulate this)
    contaminated.fold_results[0].accuracy = 0.99  # Inflated by leakage
    
    return contaminated


def inject_below_chance_into_trace(trace: MoabbExecutionTrace) -> MoabbExecutionTrace:
    """Inject below-chance accuracy — the model is worse than random.
    
    VIREON's statistics layer should detect this by comparing to chance level.
    """
    contaminated = copy.deepcopy(trace)
    
    # Make all accuracies below chance (0.5 for binary)
    for r in contaminated.fold_results:
        r.accuracy = 0.35 + np.random.default_rng(42).uniform(-0.05, 0.05)
    
    return contaminated


def inject_missing_seed_into_trace(trace: MoabbExecutionTrace) -> MoabbExecutionTrace:
    """Remove the seed from the trace.
    
    VIREON's reproducibility checks should detect this.
    """
    contaminated = copy.deepcopy(trace)
    contaminated.seed = None
    return contaminated


def inject_missing_environment_into_trace(trace: MoabbExecutionTrace) -> MoabbExecutionTrace:
    """Remove environment information from the trace.
    
    VIREON's reproducibility checks should detect this.
    """
    contaminated = copy.deepcopy(trace)
    contaminated.environment.moabb_version = "unknown"
    contaminated.environment.mne_version = "unknown"
    contaminated.environment.python_version = "unknown"
    return contaminated


def inject_impossibly_narrow_ci_into_statistics(trace: MoabbExecutionTrace) -> MoabbExecutionTrace:
    """This fault can't be injected into the trace itself — it's in the
    STATISTICS computation, not the execution trace.
    
    VIREON's statistics layer computes the CI from the fold results.
    If we inject 1000 folds all with accuracy 0.837, the CI would be
    legitimately narrow. So this fault class CANNOT be detected from
    the execution trace alone — it requires knowing the experimental
    structure (n_subjects vs n_trials).
    
    This is an important negative result.
    """
    # We can't inject this — the CI is computed FROM the fold results.
    # If we change the fold results, we're changing the data, not the statistics.
    # The pseudoreplication fault would need to be in HOW the statistics
    # are computed, not in the data itself.
    return trace  # No-op — documented as a limitation


def inject_tampered_evidence_bundle(bundle_dict: dict) -> dict:
    """Tamper with the evidence bundle after creation.
    
    VIREON's EvidenceBundle.verify() should detect this.
    """
    tampered = copy.deepcopy(bundle_dict)
    tampered["summary"]["mean_accuracy"] = 0.99
    return tampered


# ─── Run Study B ───

def run_study_b():
    """Run the end-to-end fault detection study."""
    print("=" * 70)
    print("  VIREON STUDY B — END-TO-END FAULT DETECTION")
    print("  Faults injected into RAW EXECUTION TRACE")
    print("  VIREON's actual ValidationLayer must DISCOVER them")
    print("=" * 70)
    print()

    # Load cached experiment data
    bundle_dict, spec = load_cached_trace()
    clean_trace = reconstruct_trace(bundle_dict)
    
    print("  Baseline: CSP+LDA on BNCI2014_001")
    print(f"  Mean accuracy: {clean_trace.mean_accuracy:.4f}")
    print(f"  Folds: {len(clean_trace.fold_results)}")
    print(f"  Subjects: {len(clean_trace.per_subject_accuracy)}")
    print()

    # ─── Run clean baseline ──
    print("[0] Clean baseline — VIREON validation on unmodified trace...")
    validator = ValidationLayer()
    clean_validation = validator.validate(clean_trace, spec)
    
    clean_pass = clean_validation.all_passed
    print(f"  VIREON verdict: {'PASS' if clean_pass else 'FAIL'}")
    print(f"  Data checks: {sum(1 for c in clean_validation.data_checks if c.passed)}/{len(clean_validation.data_checks)}")
    print(f"  Leakage checks: {sum(1 for c in clean_validation.leakage_checks if c.passed)}/{len(clean_validation.leakage_checks)}")
    print(f"  Repro checks: {sum(1 for c in clean_validation.reproducibility_checks if c.passed)}/{len(clean_validation.reproducibility_checks)}")
    if clean_validation.statistics:
        print(f"  Above chance: {clean_validation.statistics.chance_level_passed}")
    print()

    results = []

    # ─── Fault 1: Subject Leakage in trace ──
    print("=" * 70)
    print("  FAULT 1: SUBJECT LEAKAGE (injected into execution trace)")
    print("  Subject 1 added to BOTH train_subjects AND test_subjects of fold 0")
    print("  Accuracy inflated to 0.99 for the contaminated fold")
    print("=" * 70)
    print()

    contaminated = inject_subject_leakage_into_trace(clean_trace)
    validation = validator.validate(contaminated, spec)
    
    # What does VIREON actually detect?
    leakage_passed = all(c.passed for c in validation.leakage_checks)
    overall_passed = validation.all_passed
    
    print(f"  VIREON leakage checks: {'PASS' if leakage_passed else 'FAIL'}")
    for c in validation.leakage_checks:
        mark = "✓" if c.passed else "✗"
        print(f"    {mark} {c.name}: {c.value}")
    print(f"  VIREON overall: {'PASS' if overall_passed else 'FAIL'}")
    print()

    # Did VIREON detect the subject overlap?
    has_overlap_check = any("overlap" in c.name.lower() for c in validation.leakage_checks)
    detected = not leakage_passed
    
    print(f"  Has train/test overlap check: {has_overlap_check}")
    print(f"  Detected subject leakage: {'YES ✓' if detected else 'NO ✗'}")
    if not detected:
        print("  → VIREON's validation layer does NOT examine train/test subject overlap")
        print("  → It only checks evaluation design name, not actual partition data")
        print("  → This is a GAP — VIREON cannot discover this fault from raw data")
    
    results.append({
        "fault": "subject_leakage",
        "injected_into": "execution_trace (partitions[0].train_subjects)",
        "expected": "FAIL",
        "vireon_verdict": "PASS" if overall_passed else "FAIL",
        "detected": detected,
        "has_relevant_check": has_overlap_check,
        "note": "VIREON checks evaluation design name, not actual subject overlap" if not detected else ""
    })
    print()

    # ─── Fault 2: Below-chance accuracy ──
    print("=" * 70)
    print("  FAULT 2: BELOW-CHANCE ACCURACY (injected into fold results)")
    print("  All fold accuracies set to ~0.35 (below chance=0.50)")
    print("=" * 70)
    print()

    contaminated = inject_below_chance_into_trace(clean_trace)
    validation = validator.validate(contaminated, spec)
    
    chance_passed = validation.statistics.chance_level_passed if validation.statistics else None
    overall_passed = validation.all_passed
    
    print(f"  Mean accuracy: {contaminated.mean_accuracy:.4f}")
    print(f"  Chance level: {validation.statistics.chance_level:.4f}")
    print(f"  Above chance: {chance_passed}")
    print(f"  VIREON overall: {'PASS' if overall_passed else 'FAIL'}")
    print()

    detected = not chance_passed
    print(f"  Detected below-chance: {'YES ✓' if detected else 'NO ✗'}")
    if detected:
        print("  → VIREON's statistics layer correctly identifies accuracy < chance")
    
    results.append({
        "fault": "below_chance",
        "injected_into": "execution_trace (fold_results[*].accuracy)",
        "expected": "FAIL",
        "vireon_verdict": "PASS" if overall_passed else "FAIL",
        "detected": detected,
        "has_relevant_check": True,
        "note": "Statistics layer compares mean accuracy to chance level"
    })
    print()

    # ─── Fault 3: Missing seed ──
    print("=" * 70)
    print("  FAULT 3: MISSING SEED (removed from execution trace)")
    print("=" * 70)
    print()

    contaminated = inject_missing_seed_into_trace(clean_trace)
    validation = validator.validate(contaminated, spec)
    
    seed_check = next((c for c in validation.reproducibility_checks if "seed" in c.name.lower()), None)
    detected = seed_check and not seed_check.passed
    overall_passed = validation.all_passed
    
    print("  VIREON reproducibility checks:")
    for c in validation.reproducibility_checks:
        mark = "✓" if c.passed else "✗"
        print(f"    {mark} {c.name}: {c.value}")
    print(f"  VIREON overall: {'PASS' if overall_passed else 'FAIL'}")
    print()

    print(f"  Detected missing seed: {'YES ✓' if detected else 'NO ✗'}")
    if detected:
        print("  → VIREON's reproducibility layer correctly detects missing seed")
    
    results.append({
        "fault": "missing_seed",
        "injected_into": "execution_trace (seed = None)",
        "expected": "FAIL",
        "vireon_verdict": "PASS" if overall_passed else "FAIL",
        "detected": detected,
        "has_relevant_check": True,
        "note": "Reproducibility layer checks for seed presence"
    })
    print()

    # ─── Fault 4: Missing environment ──
    print("=" * 70)
    print("  FAULT 4: MISSING ENVIRONMENT (versions set to 'unknown')")
    print("=" * 70)
    print()

    contaminated = inject_missing_environment_into_trace(clean_trace)
    validation = validator.validate(contaminated, spec)
    
    env_check = next((c for c in validation.reproducibility_checks if "environment" in c.name.lower()), None)
    detected = env_check and not env_check.passed
    overall_passed = validation.all_passed
    
    print("  VIREON reproducibility checks:")
    for c in validation.reproducibility_checks:
        mark = "✓" if c.passed else "✗"
        print(f"    {mark} {c.name}: {c.value}")
    print(f"  VIREON overall: {'PASS' if overall_passed else 'FAIL'}")
    print()

    print(f"  Detected missing environment: {'YES ✓' if detected else 'NO ✗'}")
    if detected:
        print("  → VIREON's reproducibility layer correctly detects missing environment")
    elif not detected and env_check:
        print("  → VIREON checks environment but the check passed despite 'unknown' versions")
        print("  → This may be a gap — 'unknown' should be treated as missing")
    
    results.append({
        "fault": "missing_environment",
        "injected_into": "execution_trace (environment.*_version = 'unknown')",
        "expected": "FAIL",
        "vireon_verdict": "PASS" if overall_passed else "FAIL",
        "detected": detected,
        "has_relevant_check": True,
        "note": "Environment check looks for moabb_version != 'unknown'"
    })
    print()

    # ─── Fault 5: Tampered evidence bundle ──
    print("=" * 70)
    print("  FAULT 5: TAMPERED EVIDENCE BUNDLE")
    print("  Modified accuracy in bundle summary after creation")
    print("=" * 70)
    print()

    from vireon_moabb.evidence import EvidenceBundle
    
    tampered_dict = inject_tampered_evidence_bundle(bundle_dict)
    tampered_bundle = EvidenceBundle(
        bundle_id=tampered_dict["bundle_id"],
        evidence_hash=tampered_dict["evidence_hash"],
        created_at=tampered_dict["created_at"],
        experiment_spec=tampered_dict["experiment_spec"],
        execution_trace=tampered_dict["execution_trace"],
        validation_results=tampered_dict["validation_results"],
        summary=tampered_dict["summary"],
    )
    
    original_verify = EvidenceBundle(
        bundle_id=bundle_dict["bundle_id"],
        evidence_hash=bundle_dict["evidence_hash"],
        created_at=bundle_dict["created_at"],
        experiment_spec=bundle_dict["experiment_spec"],
        execution_trace=bundle_dict["execution_trace"],
        validation_results=bundle_dict["validation_results"],
        summary=bundle_dict["summary"],
    ).verify()
    
    tampered_verify = tampered_bundle.verify()
    
    print(f"  Original accuracy: {bundle_dict['summary']['mean_accuracy']:.4f}")
    print(f"  Tampered accuracy: {tampered_dict['summary']['mean_accuracy']:.4f}")
    print(f"  Original verify(): {original_verify}")
    print(f"  Tampered verify(): {tampered_verify}")
    print()

    detected = not tampered_verify
    print(f"  Detected tampering: {'YES ✓' if detected else 'NO ✗'}")
    if detected:
        print("  → SHA-256 hash mismatch detected — tamper protection works")
    
    results.append({
        "fault": "tampered_evidence",
        "injected_into": "evidence_bundle (summary.mean_accuracy)",
        "expected": "FAIL",
        "vireon_verdict": "PASS" if tampered_verify else "FAIL",
        "detected": detected,
        "has_relevant_check": True,
        "note": "SHA-256 hash verification detects content modification"
    })
    print()

    # ─── Summary ──
    print()
    print("=" * 70)
    print("  STUDY B SUMMARY — END-TO-END FAULT DETECTION")
    print("=" * 70)
    print()
    print("  Faults injected into RAW EXECUTION TRACE (not ValidationResult)")
    print("  VIREON's actual ValidationLayer.validate() ran on contaminated data")
    print()
    print(f"  {'Fault':25s} {'Injected Into':40s} {'Expected':8s} {'Detected':8s}")
    print(f"  {'─'*25} {'─'*40} {'─'*8} {'─'*8}")

    n_detected = 0
    n_total = len(results)
    
    for r in results:
        mark = "✓ YES" if r["detected"] else "✗ NO"
        expected = r["expected"]
        print(f"  {r['fault']:25s} {r['injected_into'][:40]:40s} {expected:8s} {mark:8s}")
        if r["detected"]:
            n_detected += 1

    print()
    print(f"  End-to-end detection rate: {n_detected}/{n_total}")
    print()

    # ─── Honest assessment ──
    print(f"  {'='*66}")
    print("  HONEST ASSESSMENT")
    print(f"  {'='*66}")
    print()

    missed = [r for r in results if not r["detected"]]
    if missed:
        print(f"  VIREON MISSED {len(missed)} fault(s) when they were injected")
        print("  into the raw execution trace:")
        print()
        for r in missed:
            print(f"    ✗ {r['fault']}: {r['note']}")
        print()

    detected_list = [r for r in results if r["detected"]]
    if detected_list:
        print(f"  VIREON DETECTED {len(detected_list)} fault(s) from raw data:")
        print()
        for r in detected_list:
            print(f"    ✓ {r['fault']}: {r['note']}")
        print()

    # ─── Comparison with Study A ──
    print(f"  {'─'*66}")
    print("  COMPARISON: STUDY A vs STUDY B")
    print(f"  {'─'*66}")
    print()
    print("  Study A (rule-engine classification): 17/17 detected (100%)")
    print("    Faults injected into: ValidationResult objects")
    print("    Tests: Can the verdict engine honor failed checks?")
    print()
    print(f"  Study B (end-to-end detection):        {n_detected}/{n_total} detected ({n_detected/n_total*100:.0f}%)")
    print("    Faults injected into: Raw execution trace")
    print("    Tests: Can VIREON DISCOVER faults from raw data?")
    print()

    if n_detected < n_total:
        gap = n_total - n_detected
        print(f"  GAP: {gap} fault(s) that VIREON can classify when given but cannot")
        print("  discover from raw execution data. These require implementing")
        print("  actual data-level detection logic in the validation layer.")
    print()

    print(f"  {'='*66}")
    print("  END OF STUDY B")
    print(f"  {'='*66}")

    # Save
    output = {
        "study": "B_end_to_end_fault_detection",
        "description": "Faults injected into raw execution trace. VIREON's actual ValidationLayer runs.",
        "baseline_accuracy": clean_trace.mean_accuracy,
        "results": results,
        "detection_rate": f"{n_detected}/{n_total}",
        "missed_faults": [r["fault"] for r in results if not r["detected"]],
        "detected_faults": [r["fault"] for r in results if r["detected"]],
    }
    output_path = os.path.join(REPO, "study_b_results.json")
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nResults saved: {output_path}")


if __name__ == "__main__":
    run_study_b()
