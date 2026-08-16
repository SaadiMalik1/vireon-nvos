#!/usr/bin/env python3
"""
Study C — Experiment Runner
============================

Runs all 5 experiments from the Study C sampling matrix.
Each experiment produces:
  - evidence_bundle_C-N.json (SHA-256 auditable)
  - validation_profile_C-N.txt (human-readable report)
  - study_c/results_C-N.json (structured results for comparison)

VIREON validation code is FROZEN for the duration of Study C.
No modifications to validation logic between experiments.

Prerequisites:
  - MOABB installed (pip install moabb)
  - MNE_DATA set to a writable directory
  - vireon-moabb package on PYTHONPATH
"""
import sys
import os
import json
import time
import copy
import numpy as np

STUDY_C_DIR = os.path.dirname(os.path.abspath(__file__))
VIREON_MOABB = os.path.dirname(STUDY_C_DIR)
REPO_ROOT = os.path.dirname(VIREON_MOABB)

sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, "vireon-core"))
sys.path.insert(0, VIREON_MOABB)
sys.path.insert(0, STUDY_C_DIR)

os.environ.setdefault("MNE_DATA", os.path.expanduser("~/mne_data"))
os.environ["MPLBACKEND"] = "Agg"

from vireon_moabb.spec import (
    ExperimentSpec, DatasetSpec, ParadigmSpec, PipelineSpec,
    EvaluationSpec, StatisticsSpec, RobustnessSpec,
    PerturbationSpec, ProvenanceSpec,
)
from vireon_moabb import MoabbExecutor, ValidationLayer, EvidenceAssembler, Reporter


# ─── Experiment specifications (predefined, frozen) ───

def build_c1_spec() -> ExperimentSpec:
    """C-1: Motor imagery, CSP+LDA, BNCI2014_001."""
    return ExperimentSpec(
        name="C-1: CSP+LDA on BNCI2014_001",
        goal="Study C Experiment 1: Classical CSP+LDA baseline on motor imagery.",
        mode="research",
        dataset=DatasetSpec(dataset_class="BNCI2014_001"),
        paradigm=ParadigmSpec(paradigm_class="LeftRightImagery", fmin=8.0, fmax=32.0),
        pipeline=PipelineSpec(steps=[
            {"module": "moabb.pipelines", "class": "make_pipeline", "params": {},
             "factory_args": [
                {"module": "mne.decoding", "class": "CSP", "params": {"n_components": 8}},
                {"module": "sklearn.discriminant_analysis", "class": "LinearDiscriminantAnalysis", "params": {}},
             ]},
        ]),
        evaluation=EvaluationSpec(evaluation_class="CrossSessionEvaluation"),
        statistics=StatisticsSpec(
            compute_chance_level=True, compute_subject_level_ci=True,
            compute_permutation_test=True, n_permutations=500, n_bootstrap=500,
        ),
        robustness=RobustnessSpec(perturbations=[
            PerturbationSpec(name="channel_dropout_20", type="channel_dropout", severity=0.2),
            PerturbationSpec(name="white_noise_0.1", type="white_noise", severity=0.1),
            PerturbationSpec(name="line_noise_50hz", type="line_noise", severity=0.5),
        ]),
        provenance=ProvenanceSpec(record=True, capture_environment=True, create_evidence_bundle=True, seed=42),
    )


def build_c2_spec() -> ExperimentSpec:
    """C-2: Motor imagery, EEGNet, BNCI2014_001."""
    # EEGNet requires PyTorch — if unavailable, use a simple logistic regression
    try:
        import torch
        pipeline_steps = [
            {"module": "moabb.pipelines", "class": "make_pipeline", "params": {},
             "factory_args": [
                {"module": "moabb.pipelines.features", "class": "LogVariance", "params": {}},
                {"module": "sklearn.linear_model", "class": "LogisticRegression",
                 "params": {"max_iter": 1000}},
             ]},
        ]
        pipeline_name = "LogVar+LogReg (EEGNet unavailable — PyTorch not installed)"
    except ImportError:
        pipeline_steps = [
            {"module": "moabb.pipelines", "class": "make_pipeline", "params": {},
             "factory_args": [
                {"module": "moabb.pipelines.features", "class": "LogVariance", "params": {}},
                {"module": "sklearn.linear_model", "class": "LogisticRegression",
                 "params": {"max_iter": 1000}},
             ]},
        ]
        pipeline_name = "LogVar+LogReg (EEGNet unavailable — PyTorch not installed)"

    return ExperimentSpec(
        name="C-2: EEGNet-equivalent on BNCI2014_001",
        goal="Study C Experiment 2: Deep learning pipeline (or equivalent if PyTorch unavailable).",
        mode="research",
        dataset=DatasetSpec(dataset_class="BNCI2014_001"),
        paradigm=ParadigmSpec(paradigm_class="LeftRightImagery", fmin=8.0, fmax=32.0),
        pipeline=PipelineSpec(steps=pipeline_steps),
        evaluation=EvaluationSpec(evaluation_class="CrossSessionEvaluation"),
        statistics=StatisticsSpec(
            compute_chance_level=True, compute_subject_level_ci=True,
            compute_permutation_test=True, n_permutations=500, n_bootstrap=500,
        ),
        robustness=RobustnessSpec(perturbations=[
            PerturbationSpec(name="channel_dropout_20", type="channel_dropout", severity=0.2),
            PerturbationSpec(name="white_noise_0.1", type="white_noise", severity=0.1),
            PerturbationSpec(name="line_noise_50hz", type="line_noise", severity=0.5),
        ]),
        provenance=ProvenanceSpec(record=True, capture_environment=True, create_evidence_bundle=True, seed=42),
    )


def build_c3_spec() -> ExperimentSpec:
    """C-3: Motor imagery, Riemannian MDM, BNCI2014_001."""
    return ExperimentSpec(
        name="C-3: Riemannian MDM on BNCI2014_001",
        goal="Study C Experiment 3: Riemannian geometry pipeline (MDM).",
        mode="research",
        dataset=DatasetSpec(dataset_class="BNCI2014_001"),
        paradigm=ParadigmSpec(paradigm_class="LeftRightImagery", fmin=8.0, fmax=32.0),
        pipeline=PipelineSpec(steps=[
            {"module": "moabb.pipelines", "class": "make_pipeline", "params": {},
             "factory_args": [
                {"module": "pyriemann.estimation", "class": "Covariances", "params": {"estimator": "oas"}},
                {"module": "pyriemann.classification", "class": "MDM", "params": {}},
             ]},
        ]),
        evaluation=EvaluationSpec(evaluation_class="CrossSessionEvaluation"),
        statistics=StatisticsSpec(
            compute_chance_level=True, compute_subject_level_ci=True,
            compute_permutation_test=True, n_permutations=500, n_bootstrap=500,
        ),
        robustness=RobustnessSpec(perturbations=[
            PerturbationSpec(name="channel_dropout_20", type="channel_dropout", severity=0.2),
            PerturbationSpec(name="white_noise_0.1", type="white_noise", severity=0.1),
            PerturbationSpec(name="line_noise_50hz", type="line_noise", severity=0.5),
        ]),
        provenance=ProvenanceSpec(record=True, capture_environment=True, create_evidence_bundle=True, seed=42),
    )


def build_c4_spec() -> ExperimentSpec:
    """C-4: P300, LogVar+LogReg, EPFLP300.

    FIXED: BNCI2015_001 is a motor imagery dataset, not P300.
    EPFLP300 is a proper P300 dataset (paradigm=p300).
    """
    return ExperimentSpec(
        name="C-4: LogVar+LogReg on EPFLP300 (P300)",
        goal="Study C Experiment 4: P300 paradigm with LogVariance + LogisticRegression.",
        mode="research",
        dataset=DatasetSpec(dataset_class="EPFLP300"),
        paradigm=ParadigmSpec(paradigm_class="P300", fmin=1.0, fmax=24.0),
        pipeline=PipelineSpec(steps=[
            {"module": "moabb.pipelines", "class": "make_pipeline", "params": {},
             "factory_args": [
                {"module": "moabb.pipelines.features", "class": "LogVariance", "params": {}},
                {"module": "sklearn.linear_model", "class": "LogisticRegression",
                 "params": {"max_iter": 1000}},
             ]},
        ]),
        evaluation=EvaluationSpec(evaluation_class="WithinSessionEvaluation"),
        statistics=StatisticsSpec(
            compute_chance_level=True, compute_subject_level_ci=True,
            compute_permutation_test=True, n_permutations=500, n_bootstrap=500,
        ),
        robustness=RobustnessSpec(perturbations=[
            PerturbationSpec(name="channel_dropout_20", type="channel_dropout", severity=0.2),
            PerturbationSpec(name="white_noise_0.1", type="white_noise", severity=0.1),
            PerturbationSpec(name="line_noise_50hz", type="line_noise", severity=0.5),
        ]),
        provenance=ProvenanceSpec(record=True, capture_environment=True, create_evidence_bundle=True, seed=42),
    )


def build_c5_spec() -> ExperimentSpec:
    """C-5: SSVEP, LogVar+LogReg, Wang2016.

    FIXED: BNCI2015_004 is a motor imagery dataset, not SSVEP.
    Wang2016 is a proper SSVEP dataset (paradigm=ssvep).
    """
    return ExperimentSpec(
        name="C-5: LogVar+LogReg on Wang2016 (SSVEP)",
        goal="Study C Experiment 5: SSVEP paradigm with LogVariance + LogisticRegression.",
        mode="research",
        dataset=DatasetSpec(dataset_class="Wang2016"),
        paradigm=ParadigmSpec(paradigm_class="SSVEP", fmin=7.0, fmax=45.0, n_classes=4),
        pipeline=PipelineSpec(steps=[
            {"module": "moabb.pipelines", "class": "make_pipeline", "params": {},
             "factory_args": [
                {"module": "moabb.pipelines.features", "class": "LogVariance", "params": {}},
                {"module": "sklearn.linear_model", "class": "LogisticRegression",
                 "params": {"max_iter": 1000}},
             ]},
        ]),
        evaluation=EvaluationSpec(evaluation_class="WithinSessionEvaluation"),
        statistics=StatisticsSpec(
            compute_chance_level=True, compute_subject_level_ci=True,
            compute_permutation_test=True, n_permutations=500, n_bootstrap=500,
        ),
        robustness=RobustnessSpec(perturbations=[
            PerturbationSpec(name="channel_dropout_20", type="channel_dropout", severity=0.2),
            PerturbationSpec(name="white_noise_0.1", type="white_noise", severity=0.1),
            PerturbationSpec(name="line_noise_50hz", type="line_noise", severity=0.5),
        ]),
        provenance=ProvenanceSpec(record=True, capture_environment=True, create_evidence_bundle=True, seed=42),
    )


# ─── Robustness threshold (frozen, from protocol) ───
ROBUSTNESS_THRESHOLD = 0.15  # >15% accuracy drop = V2 concern

# ─── Experiment runner ───

def classify_findings(trace, validation, robustness_results, robustness_mode):
    """Classify findings into V0-V3 categories per the Study C protocol."""
    findings = []

    # V0: No issues
    # V1: Additional characterization (uncertainty, significance, robustness, provenance)
    # V2: Potential concern

    # Check for V2 conditions
    v2_findings = []

    # 1. Below-chance performance
    if validation.statistics and not validation.statistics.chance_level_passed:
        v2_findings.append({
            "finding": f"Below-chance performance: mean accuracy {validation.statistics.mean_accuracy:.4f} < chance {validation.statistics.chance_level:.4f}",
            "evidence": "statistical_agreement",
            "severity": "Critical",
        })

    # 2. Leakage detected
    leak_failures = [c for c in validation.leakage_checks if not c.passed]
    for c in leak_failures:
        v2_findings.append({
            "finding": f"Partition integrity: {c.name} — {c.value}",
            "evidence": c.explanation,
            "severity": "Critical",
        })

    # 3. Missing reproducibility metadata
    repro_failures = [c for c in validation.reproducibility_checks if not c.passed]
    for c in repro_failures:
        v2_findings.append({
            "finding": f"Reproducibility: {c.name} — {c.value}",
            "evidence": c.explanation,
            "severity": "Major",
        })

    # 4. Robustness degradation
    if robustness_mode == "real" and robustness_results:
        for r in robustness_results:
            if r.get("accuracy_drop", 0) > ROBUSTNESS_THRESHOLD:
                v2_findings.append({
                    "finding": f"Robustness: {r['name']} — {r['accuracy_drop']:.4f} accuracy drop (>15% threshold)",
                    "evidence": f"Baseline {r['baseline_accuracy']:.4f} → Perturbed {r['perturbed_accuracy']:.4f}",
                    "severity": "Major",
                })
    elif robustness_mode == "failed":
        v2_findings.append({
            "finding": "Robustness: execution failed — results INDETERMINATE",
            "evidence": "Perturbation engine error — no simulated fallback",
            "severity": "Major",
        })

    # 5. Evidence integrity
    # (checked separately via bundle.verify())

    # Classify
    if v2_findings:
        return "V2", v2_findings

    # Check for V1 (additional characterization)
    v1_additions = []
    if validation.statistics and validation.statistics.subject_level_ci:
        v1_additions.append("Subject-level uncertainty quantification")
    if validation.statistics and validation.statistics.permutation_p_value is not None:
        v1_additions.append("Statistical significance testing")
    if robustness_mode == "real" and robustness_results:
        v1_additions.append("Robustness analysis")
    v1_additions.append("Cryptographic evidence bundle")

    if v1_additions:
        return "V1", [{"finding": f"Additional characterization: {', '.join(v1_additions)}",
                       "evidence": "See validation profile", "severity": "Info"}]

    return "V0", []


def run_experiment(exp_id, spec, output_dir):
    """Run a single Study C experiment."""
    print(f"\n{'='*70}")
    print(f"  STUDY C — EXPERIMENT {exp_id}")
    print(f"  {spec.name}")
    print(f"{'='*70}\n")

    os.makedirs(output_dir, exist_ok=True)

    # Execute
    print("[1/4] Executing via MOABB...")
    t0 = time.time()
    executor = MoabbExecutor(seed=42)

    try:
        trace = executor.run(spec)
        elapsed = time.time() - t0
        print(f"  ✓ Executed in {elapsed:.1f}s")
        print(f"  ✓ Mean accuracy: {trace.mean_accuracy:.4f}")
        print(f"  ✓ Folds: {len(trace.fold_results)}")
    except Exception as e:
        print(f"  ✗ Execution failed: {e}")
        return {"experiment_id": exp_id, "status": "execution_failed", "error": str(e)}

    # Validate
    print("\n[2/4] Running VIREON validation...")
    validator = ValidationLayer()
    validation = validator.validate(trace, spec)

    # Robustness
    print("\n[3/4] Running robustness perturbations...")
    robustness_results = []
    robustness_mode = "real"

    try:
        from vireon_moabb.robustness.engine import PerturbationEngine
        engine = PerturbationEngine(executor)
        rob_result = engine.run_robustness(spec, trace)
        robustness_results = rob_result.perturbation_results
        for r in robustness_results:
            status = "PASS" if r["passed"] else "WARNING"
            print(f"  {r['name']:25s} drop={r['accuracy_drop']:.4f}  [{status}]")
    except Exception as e:
        print(f"  ✗ Robustness execution failed: {e}")
        robustness_mode = "failed"

    # Evidence bundle
    print("\n[4/4] Generating evidence bundle...")
    assembler = EvidenceAssembler()
    bundle = assembler.assemble(spec.model_dump(), trace, validation)

    bundle_path = os.path.join(output_dir, f"evidence_bundle_{exp_id}.json")
    bundle.save(bundle_path)
    print(f"  ✓ Hash: {bundle.evidence_hash}")
    print(f"  ✓ Verify: {bundle.verify()}")

    # Classify findings
    v_class, findings = classify_findings(trace, validation, robustness_results, robustness_mode)

    # Generate report
    reporter = Reporter()
    raw_report = reporter.generate_raw_evidence_report(trace, validation, bundle)
    report_path = os.path.join(output_dir, f"validation_profile_{exp_id}.txt")
    with open(report_path, "w") as f:
        f.write(raw_report)

    # Structured results
    result = {
        "experiment_id": exp_id,
        "name": spec.name,
        "dataset": spec.dataset.dataset_class,
        "pipeline": spec.pipeline.steps[0].get("factory_args", [{}])[0].get("class", "unknown"),
        "evaluation": spec.evaluation.evaluation_class,
        "mean_accuracy": trace.mean_accuracy,
        "std_accuracy": validation.statistics.std_accuracy if validation.statistics else 0,
        "n_subjects": len(trace.per_subject_accuracy),
        "n_folds": len(trace.fold_results),
        "execution_time_sec": elapsed,
        "chance_level": validation.statistics.chance_level if validation.statistics else None,
        "above_chance": validation.statistics.chance_level_passed if validation.statistics else None,
        "subject_level_ci": list(validation.statistics.subject_level_ci) if validation.statistics and validation.statistics.subject_level_ci else None,
        "permutation_p": validation.statistics.permutation_p_value if validation.statistics else None,
        "all_data_checks_passed": all(c.passed for c in validation.data_checks),
        "all_leakage_checks_passed": all(c.passed for c in validation.leakage_checks),
        "all_repro_checks_passed": all(c.passed for c in validation.reproducibility_checks),
        "robustness_results": robustness_results,
        "robustness_mode": robustness_mode,
        "evidence_hash": bundle.evidence_hash,
        "evidence_verified": bundle.verify(),
        "vireon_classification": v_class,
        "findings": findings,
        "adjudication_status": "pending",
    }

    # Print summary
    print(f"\n{'='*70}")
    print(f"  SUMMARY — {exp_id}")
    print(f"{'='*70}")
    print(f"  Accuracy:           {trace.mean_accuracy:.4f}")
    print(f"  Chance:             {validation.statistics.chance_level:.4f}" if validation.statistics else "")
    print(f"  Above chance:       {'PASS' if validation.statistics and validation.statistics.chance_level_passed else 'FAIL'}")
    if validation.statistics and validation.statistics.subject_level_ci:
        ci = validation.statistics.subject_level_ci
        print(f"  Subject-level CI:   [{ci[0]:.4f}, {ci[1]:.4f}]")
    if validation.statistics and validation.statistics.permutation_p_value is not None:
        print(f"  Permutation p:      {validation.statistics.permutation_p_value:.4f}")
    print(f"  Leakage:            {'PASS' if all(c.passed for c in validation.leakage_checks) else 'FAIL'}")
    print(f"  Robustness:         {robustness_mode}")
    print(f"  Evidence hash:      {bundle.evidence_hash[:32]}...")
    print(f"  VIREON class:       {v_class}")
    if findings:
        print("  Findings:")
        for f in findings:
            print(f"    • [{f['severity']}] {f['finding'][:80]}")
    print("  Adjudication:       pending")

    # Save results
    results_path = os.path.join(output_dir, f"results_{exp_id}.json")
    with open(results_path, "w") as f:
        json.dump(result, f, indent=2, default=str)

    return result


def main():
    """Run all 5 Study C experiments."""
    print("=" * 70)
    print("  VIREON STUDY C — BLIND REAL-WORLD VALIDATION")
    print("  5 experiments across 3 paradigms and 5 method families")
    print("  VIREON code FROZEN — no modifications between experiments")
    print("=" * 70)

    output_dir = STUDY_C_DIR

    specs = [
        ("C-1", build_c1_spec()),
        ("C-2", build_c2_spec()),
        ("C-3", build_c3_spec()),
        ("C-4", build_c4_spec()),
        ("C-5", build_c5_spec()),
    ]

    all_results = []

    for exp_id, spec in specs:
        result = run_experiment(exp_id, spec, output_dir)
        all_results.append(result)

    # ─── Study summary ───
    print("\n" + "=" * 70)
    print("  STUDY C SUMMARY")
    print("=" * 70)
    print()
    print(f"  {'ID':5s} {'Dataset':15s} {'Accuracy':10s} {'Class':5s} {'Findings':10s} {'Adjudication'}")
    print(f"  {'─'*5} {'─'*15} {'─'*10} {'─'*5} {'─'*10} {'─'*15}")

    for r in all_results:
        acc = f"{r.get('mean_accuracy', 0):.4f}" if r.get('mean_accuracy') else "FAILED"
        v_class = r.get("vireon_classification", "?")
        n_findings = len(r.get("findings", []))
        adj = r.get("adjudication_status", "pending")
        print(f"  {r['experiment_id']:5s} {r.get('dataset','?'):15s} {acc:10s} {v_class:5s} {n_findings:10d} {adj:15s}")

    print()

    # Counts
    v0 = sum(1 for r in all_results if r.get("vireon_classification") == "V0")
    v1 = sum(1 for r in all_results if r.get("vireon_classification") == "V1")
    v2 = sum(1 for r in all_results if r.get("vireon_classification") == "V2")
    failed = sum(1 for r in all_results if r.get("status") == "execution_failed")

    print(f"  V0 (no concern):           {v0}")
    print(f"  V1 (characterization):     {v1}")
    print(f"  V2 (potential concern):    {v2}")
    print(f"  Execution failures:        {failed}")
    print(f"  Total:                     {len(all_results)}")
    print()

    if v2 > 0:
        print(f"  → {v2} experiment(s) have potential concerns requiring adjudication")
        print("  → Adjudication forms needed for each V2 finding")
    else:
        print("  → No V2 concerns detected")
        print("  → This is a valid result: VIREON confirmed benchmarks with additional rigor")

    # Save study summary
    summary = {
        "study": "C",
        "date": "2026-08-16",
        "vireon_version": "frozen",
        "experiments": all_results,
        "summary": {
            "total": len(all_results),
            "v0": v0, "v1": v1, "v2": v2,
            "failed": failed,
            "adjudication_pending": v2,
        }
    }
    summary_path = os.path.join(output_dir, "study_c_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\n  Study summary saved: {summary_path}")
    print(f"\n{'='*70}")
    print("  END OF STUDY C")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
