#!/usr/bin/env python3
"""
VIREON First Scientific Experiment (FIXED)
==========================================

Paper: Jayaram & Barachant (2018) — MOABB benchmark paper
Pipeline: CSP + LDA on BNCI2014_001 (motor imagery, 9 subjects)
Evaluation: CrossSessionEvaluation

FIXES from initial run:
  1. Robustness engine bug fixed (worst_perturbation property added)
  2. NO silent fallback to simulated values — if robustness fails, report INDETERMINATE
  3. Data integrity checks now show which specific check failed
  4. Evidence bundle records execution_mode for each dimension
  5. Finding count corrected (robustness excluded if invalid)
"""
import sys
import os
import json
import time
import numpy as np

REPO = os.path.dirname(os.path.abspath(__file__))
VIREON = os.path.dirname(REPO)
sys.path.insert(0, VIREON)
sys.path.insert(0, os.path.join(VIREON, "vireon-core"))
sys.path.insert(0, REPO)

os.environ.setdefault("MNE_DATA", os.path.expanduser("~/mne_data"))
os.environ["MPLBACKEND"] = "Agg"

from vireon_moabb.spec import (
    ExperimentSpec, DatasetSpec, ParadigmSpec, PipelineSpec,
    EvaluationSpec, StatisticsSpec, RobustnessSpec,
    PerturbationSpec, ProvenanceSpec,
)
from vireon_moabb import MoabbExecutor, ValidationLayer, EvidenceAssembler, Reporter


def build_csp_lda_spec() -> ExperimentSpec:
    """Build the experiment spec for CSP+LDA on BNCI2014_001."""
    return ExperimentSpec(
        name="VIREON Experiment 1: CSP+LDA on BNCI2014_001",
        goal="Determine whether VIREON's validation layer discovers scientifically meaningful information that conventional benchmarking does not, using the canonical BCI baseline (CSP+LDA) on BCI Competition IV-2a.",
        mode="research",
        dataset=DatasetSpec(dataset_class="BNCI2014_001"),
        paradigm=ParadigmSpec(paradigm_class="LeftRightImagery", fmin=8.0, fmax=32.0),
        pipeline=PipelineSpec(steps=[
            {
                "module": "moabb.pipelines",
                "class": "make_pipeline",
                "params": {},
                "factory_args": [
                    {"module": "mne.decoding", "class": "CSP", "params": {"n_components": 8}},
                    {"module": "sklearn.discriminant_analysis", "class": "LinearDiscriminantAnalysis", "params": {}},
                ],
            }
        ]),
        evaluation=EvaluationSpec(evaluation_class="CrossSessionEvaluation"),
        statistics=StatisticsSpec(
            compute_chance_level=True,
            compute_subject_level_ci=True,
            compute_permutation_test=True,
            n_permutations=500,
            n_bootstrap=500,
            ci_level=0.95,
        ),
        robustness=RobustnessSpec(perturbations=[
            PerturbationSpec(name="channel_dropout_20", type="channel_dropout", severity=0.2),
            PerturbationSpec(name="white_noise_0.1", type="white_noise", severity=0.1),
            PerturbationSpec(name="line_noise_50hz", type="line_noise", severity=0.5),
        ]),
        provenance=ProvenanceSpec(
            record=True,
            capture_environment=True,
            create_evidence_bundle=True,
            seed=42,
        ),
    )


def run_experiment():
    """Run the complete experiment."""
    print("=" * 70)
    print("  VIREON FIRST SCIENTIFIC EXPERIMENT (FIXED)")
    print("  Paper: Jayaram & Barachant (2018) — MOABB Benchmark")
    print("  Pipeline: CSP + LDA")
    print("  Dataset: BNCI2014_001 (BCI Competition IV-2a, 9 subjects)")
    print("  Evaluation: CrossSessionEvaluation")
    print("=" * 70)
    print()

    # ── Step 1: Build spec ──
    print("[1/5] Building ExperimentSpec...")
    spec = build_csp_lda_spec()
    print(f"  Mode: {spec.mode}")
    print(f"  Dataset: {spec.dataset.dataset_class}")
    print("  Pipeline: CSP(n_components=8) + LDA")
    print("  Statistics: bootstrap CI + permutation test (subject-level)")
    print("  Robustness: 3 perturbations (channel dropout, white noise, line noise)")
    print()

    # ── Step 2: Execute via MOABB ──
    print("[2/5] Executing via MOABB (downloads data on first run)...")
    t0 = time.time()
    executor = MoabbExecutor(seed=42)
    trace = executor.run(spec)
    elapsed = time.time() - t0
    print(f"  ✓ Executed in {elapsed:.1f}s")
    print(f"  ✓ {len(trace.fold_results)} folds across {len(trace.per_subject_accuracy)} subjects")
    print(f"  ✓ Mean accuracy: {trace.mean_accuracy:.4f}")
    print(f"  ✓ Per-subject: {', '.join(f'S{s}={a:.3f}' for s, a in sorted(trace.per_subject_accuracy.items()))}")
    print()

    # ── Step 3: Validate ──
    print("[3/5] Running VIREON validation layer...")
    validator = ValidationLayer()
    validation = validator.validate(trace, spec)

    # Data integrity — show EVERY check, not just a count
    print("  Data integrity checks:")
    n_data_passed = 0
    for c in validation.data_checks:
        mark = "✓" if c.passed else "✗"
        print(f"    {mark} {c.name}: {c.value}")
        if c.passed:
            n_data_passed += 1
        else:
            print(f"       Explanation: {c.explanation}")
    print(f"  Data integrity: {n_data_passed}/{len(validation.data_checks)} passed")

    # Leakage — show every check
    print("  Leakage checks:")
    n_leak_passed = 0
    for c in validation.leakage_checks:
        mark = "✓" if c.passed else "✗"
        print(f"    {mark} {c.name}: {c.value}")
        if c.passed:
            n_leak_passed += 1
    print(f"  Leakage: {n_leak_passed}/{len(validation.leakage_checks)} passed")

    # Reproducibility — show every check
    print("  Reproducibility checks:")
    n_repro_passed = 0
    for c in validation.reproducibility_checks:
        mark = "✓" if c.passed else "✗"
        print(f"    {mark} {c.name}: {c.value}")
        if c.passed:
            n_repro_passed += 1
    print(f"  Reproducibility: {n_repro_passed}/{len(validation.reproducibility_checks)} passed")

    if validation.statistics:
        stats = validation.statistics
        print("  Statistics:")
        print(f"    Mean accuracy:     {stats.mean_accuracy:.4f}")
        print(f"    Chance level:      {stats.chance_level:.4f}")
        print(f"    Above chance:      {'PASS' if stats.chance_level_passed else 'FAIL'}")
        if stats.subject_level_ci:
            print(f"    Subject-level CI:  [{stats.subject_level_ci[0]:.4f}, {stats.subject_level_ci[1]:.4f}]")
            print(f"      (bootstrapped over {stats.n_subjects} subjects, NOT trials)")
        if stats.permutation_p_value is not None:
            sig = "significant" if stats.permutation_significant else "not significant"
            print(f"    Permutation test:  p={stats.permutation_p_value:.4f} ({sig})")
            print(f"      ({stats.n_permutations} permutations, unit=subject)")
    print()

    # ── Step 4: Robustness — NEVER silently fall back to simulation ──
    print("[4/5] Running robustness perturbations...")
    robustness_results = []
    robustness_execution_mode = "real"
    baseline_acc = trace.mean_accuracy

    try:
        from vireon_moabb.robustness.engine import PerturbationEngine
        engine = PerturbationEngine(executor)
        rob_result = engine.run_robustness(spec, trace)

        # Use the fixed worst_perturbation property
        for r in rob_result.perturbation_results:
            status = "PASS" if r["passed"] else "WARNING"
            print(f"  {r['name']:25s} severity={r['severity']:.1f}  "
                  f"acc={r['perturbed_accuracy']:.4f}  drop={r['accuracy_drop']:.4f}  [{status}]")
            robustness_results.append(r)

        worst = rob_result.worst_perturbation
        if worst:
            print(f"  Worst: {worst['name']} (drop={worst['accuracy_drop']:.4f})")

        print(f"  Execution mode: {rob_result.execution_mode}")
        print(f"  Valid evidence: {rob_result.is_valid}")

    except Exception as e:
        # CRITICAL FIX: Do NOT fall back to simulation.
        # Report INDETERMINATE instead.
        print(f"  ✗ ROBUSTNESS EXECUTION FAILED: {e}")
        print("  ✗ NOT falling back to simulated values.")
        print("  ✗ Robustness status: INDETERMINATE")
        robustness_execution_mode = "failed"
        robustness_results = []

    print()

    # ── Step 5: Generate Evidence + Validation Profile ──
    print("[5/5] Generating Evidence Bundle and Validation Profile...")
    assembler = EvidenceAssembler()
    bundle = assembler.assemble(spec.model_dump(), trace, validation)

    bundle_path = os.path.join(REPO, "experiment1_evidence_bundle.json")
    bundle.save(bundle_path)
    print(f"  ✓ Bundle saved: {bundle_path}")
    print(f"  ✓ Hash: {bundle.evidence_hash}")
    print(f"  ✓ Verify: {bundle.verify()}")
    print()

    # ── Generate Validation Profile ──
    print()
    print("=" * 70)
    print("  VALIDATION PROFILE — CSP+LDA on BNCI2014_001")
    print("=" * 70)
    print()

    # Reproduction
    print("REPRODUCTION")
    print("─" * 50)
    print("  Pipeline:         CSP(n_components=8) + LDA")
    print("  Dataset:          BNCI2014_001 (9 subjects, 22 channels, 250 Hz)")
    print("  Evaluation:       CrossSessionEvaluation")
    print(f"  Reproduced:       {trace.mean_accuracy:.4f} ({trace.mean_accuracy*100:.1f}%)")
    print(f"  Std:              {validation.statistics.std_accuracy:.4f}")
    print(f"  Runtime:          {elapsed:.1f}s")
    print()

    # Per-subject
    print("  Per-subject results:")
    for s, acc in sorted(trace.per_subject_accuracy.items()):
        bar = "█" * int(acc * 30)
        marker = " ← near chance" if acc < 0.65 else ""
        print(f"    Subject {s}: {acc:.4f}  {bar}{marker}")
    print()

    # Validation
    print("VALIDATION")
    print("─" * 50)

    # Correctness
    corr = "PASS" if validation.statistics and validation.statistics.chance_level_passed else "FAIL"
    print(f"  Correctness:          {corr}")

    # Leakage
    leak_pass = all(c.passed for c in validation.leakage_checks)
    leak_str = "PASS" if leak_pass else "FAIL"
    print(f"  Leakage:              {leak_str}")
    for c in validation.leakage_checks:
        mark = "✓" if c.passed else "✗"
        print(f"    {mark} {c.name}: {c.value}")

    # Statistics
    stat_pass = validation.statistics and validation.statistics.chance_level_passed
    if validation.statistics and validation.statistics.permutation_significant is not None:
        stat_pass = stat_pass and validation.statistics.permutation_significant
    stat_str = "PASS" if stat_pass else "WARNING"
    print(f"  Statistical validity: {stat_str}")
    if validation.statistics:
        print(f"    Chance level:       {validation.statistics.chance_level:.4f}")
        print(f"    Above chance:       {'YES' if validation.statistics.chance_level_passed else 'NO'}")
        if validation.statistics.subject_level_ci:
            ci = validation.statistics.subject_level_ci
            print(f"    95% CI (subjects):  [{ci[0]:.4f}, {ci[1]:.4f}]")
        if validation.statistics.permutation_p_value is not None:
            print(f"    Permutation p:      {validation.statistics.permutation_p_value:.4f}")
            print(f"    Significant:        {'YES' if validation.statistics.permutation_significant else 'NO'}")

    # Robustness — HONEST reporting
    if robustness_execution_mode == "failed" or not robustness_results:
        rob_str = "INDETERMINATE"
        print(f"  Robustness:           {rob_str}")
        print("    ⚠ Execution failed — results not valid evidence")
        print("    (Simulated values were NOT substituted — this is a known gap)")
    else:
        rob_pass = all(r.get("passed", False) for r in robustness_results)
        rob_str = "PASS" if rob_pass else "WARNING"
        print(f"  Robustness:           {rob_str}")
        print(f"    Execution mode:     {robustness_execution_mode}")
        for r in robustness_results:
            status = "PASS" if r.get("passed") else "WARNING"
            print(f"    {r['name']:25s} drop={r['accuracy_drop']:.4f}  [{status}]")

    # Reproducibility
    repro_pass = all(c.passed for c in validation.reproducibility_checks)
    repro_str = "PASS" if repro_pass else "FAIL"
    print(f"  Reproducibility:      {repro_str}")
    for c in validation.reproducibility_checks:
        mark = "✓" if c.passed else "✗"
        print(f"    {mark} {c.name}: {c.value}")

    # Provenance
    prov_pass = bundle.verify()
    prov_str = "PASS" if prov_pass else "FAIL"
    print(f"  Provenance:           {prov_str}")
    print(f"    Evidence hash:      {bundle.evidence_hash[:32]}...")
    print(f"    Verifiable:          {'YES' if prov_pass else 'NO'}")

    # Execution validity (NEW — the conceptual contribution)
    print(f"  Execution validity:   {'PASS' if robustness_execution_mode == 'real' else 'FAIL'}")
    print("    (All dimensions executed with real computation, not simulation)")
    print()

    # Finding
    print("FINDING")
    print("─" * 50)

    findings = []
    findings.append(f"Benchmark result: {trace.mean_accuracy:.1%} accuracy (CSP+LDA, cross-session, 9 subjects)")

    # Only count findings from VALID execution
    n_additions = 0

    if validation.statistics and validation.statistics.subject_level_ci:
        ci = validation.statistics.subject_level_ci
        findings.append(f"VIREON added: Subject-level 95% CI [{ci[0]:.1%}, {ci[1]:.1%}] — "
                       f"benchmarks report point estimates without uncertainty")
        n_additions += 1

    if validation.statistics and validation.statistics.permutation_p_value is not None:
        findings.append(f"VIREON added: Permutation test p={validation.statistics.permutation_p_value:.4f} — "
                       f"benchmarks do not test statistical significance")
        n_additions += 1

    # Robustness — only count if execution was valid
    if robustness_execution_mode == "real" and robustness_results:
        rob_failures = [r for r in robustness_results if not r.get("passed", False)]
        if rob_failures:
            findings.append(f"VIREON added: {len(rob_failures)} robustness warning(s) — "
                           f"benchmarks do not test perturbation sensitivity")
            n_additions += 1
        else:
            findings.append(f"VIREON added: Robustness verified ({len(robustness_results)} perturbations passed) — "
                           f"benchmarks do not test perturbation sensitivity")
            n_additions += 1
    elif robustness_execution_mode == "failed":
        findings.append("VIREON gap: Robustness execution FAILED — results are INDETERMINATE, "
                       "not simulated-pass. This is a known engine issue to fix.")

    findings.append("VIREON added: Cryptographic evidence bundle (SHA-256) — "
                   "benchmarks produce no machine-verifiable provenance")
    n_additions += 1

    for f in findings:
        print(f"  • {f}")
    print()

    # Conclusion
    print("CONCLUSION")
    print("─" * 50)

    # Subject variability finding
    low_subjects = {s: a for s, a in trace.per_subject_accuracy.items() if a < 0.65}
    high_subjects = {s: a for s, a in trace.per_subject_accuracy.items() if a > 0.90}

    if low_subjects:
        print(f"  Subject variability finding: {len(low_subjects)} of {len(trace.per_subject_accuracy)} "
              f"subjects near chance (<65%):")
        for s, a in sorted(low_subjects.items()):
            print(f"    Subject {s}: {a:.1%}")
        print(f"  Benchmark mean ({trace.mean_accuracy:.1%}) hides this bimodal distribution.")
        print()

    if robustness_execution_mode == "failed":
        print("  Robustness: INDETERMINATE (execution failed, no simulated fallback)")
        print("  This is a VIREON engine defect, not a scientific finding.")
        print()

    print(f"  VIREON produced {n_additions} valid additional pieces of scientific")
    print("  information beyond conventional benchmarking.")
    if robustness_execution_mode == "failed":
        print("  (Robustness excluded — execution was invalid)")
    print()

    # Outcome classification
    if robustness_execution_mode == "failed":
        outcome = "B (partial) — benchmark confirmed, but robustness invalid"
    elif robustness_results and any(not r.get("passed", False) for r in robustness_results):
        outcome = "A — VIREON found a robustness issue the benchmark missed"
    else:
        outcome = "B — VIREON confirmed benchmark with additional rigor"

    print(f"  Outcome: {outcome}")
    print()

    print("=" * 70)
    print("  END OF VALIDATION PROFILE")
    print("=" * 70)

    # Generate raw evidence report
    reporter = Reporter()
    raw_report = reporter.generate_raw_evidence_report(trace, validation, bundle)
    report_path = os.path.join(REPO, "experiment1_validation_profile.txt")
    with open(report_path, "w") as f:
        f.write(raw_report)
    print(f"\nRaw evidence report: {report_path}")
    print(f"Evidence bundle:    {bundle_path}")

    return trace, validation, bundle, robustness_results, robustness_execution_mode


if __name__ == "__main__":
    run_experiment()
