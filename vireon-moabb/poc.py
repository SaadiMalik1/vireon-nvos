#!/usr/bin/env python3
"""
VIREON × MOABB — Proof of Concept

Runs ONE complete experiment end-to-end:
  ExperimentSpec
       ↓
  MOABB execution (BNCI2014_001, LeftRightImagery, LogVariance+LDA, CrossSession)
       ↓
  VIREON validation (leakage, statistics, reproducibility)
       ↓
  Evidence bundle (SHA-256)
       ↓
  Raw evidence report (NO scorecard — principle #9)

This is the smallest vertical slice that proves the architecture works.
"""
import sys
import os

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from vireon_moabb import (
    MoabbExecutor, ValidationLayer, EvidenceAssembler, Reporter,
    standard_spec,
)


def main():
    print("=" * 60)
    print("  VIREON × MOABB — Proof of Concept")
    print("=" * 60)
    print()
    print("  Architecture: ADR 0008")
    print("  Dataset: BNCI2014_001 (BCI Competition IV-2a)")
    print("  Paradigm: LeftRightImagery (8-32 Hz)")
    print("  Pipeline: LogVariance + LDA")
    print("  Evaluation: CrossSessionEvaluation")
    print()
    print("  Principles:")
    print("    1. VIREON owns experiment spec + validation + evidence")
    print("    2. MOABB owns BCI dataset/paradigm/pipeline/evaluation")
    print("    3. VIREON may instrument execution (not just final results)")
    print("    4. No scorecard — raw evidence report first")
    print("    5. Every claim traces to an execution artifact")
    print()
    print("-" * 60)
    print()

    # 1. Build the experiment spec
    print("[1/5] Building ExperimentSpec...")
    spec = standard_spec(
        dataset="BNCI2014_001",
        subject=None,  # All 9 subjects
        pipeline_name="logvar_lda",
        goal="Validate LogVariance+LDA on BCI Competition IV-2a motor imagery with cross-session evaluation",
    )
    print(f"  Mode: {spec.mode}")
    print(f"  Dataset: {spec.dataset.dataset_class}")
    print(f"  Pipeline: {len(spec.pipeline.steps[0].get('factory_args', []))} steps")
    print()

    # 2. Execute via MOABB
    print("[2/5] Executing via MOABB (this downloads data and runs the benchmark)...")
    print("  (First run downloads ~1.5 GB of EEG data from PhysioNet)")
    print()
    executor = MoabbExecutor(seed=42)
    trace = executor.run(spec)
    print(f"  ✓ Executed {len(trace.fold_results)} folds")
    print(f"  ✓ {trace.dataset_metadata.n_subjects} subjects")
    print(f"  ✓ Mean accuracy: {trace.mean_accuracy:.4f}")
    print()

    # 3. Validate
    print("[3/5] Validating execution trace...")
    validator = ValidationLayer()
    validation = validator.validate(trace, spec)
    n_data = len(validation.data_checks)
    n_leakage = len(validation.leakage_checks)
    n_repro = len(validation.reproducibility_checks)
    print(f"  ✓ {n_data} data integrity checks")
    print(f"  ✓ {n_leakage} leakage checks")
    print(f"  ✓ {n_repro} reproducibility checks")
    if validation.statistics:
        print(f"  ✓ Statistics: mean={validation.statistics.mean_accuracy:.4f}, "
              f"chance={validation.statistics.chance_level:.4f}")
        if validation.statistics.subject_level_ci:
            ci = validation.statistics.subject_level_ci
            print(f"  ✓ Subject-level CI: [{ci[0]:.4f}, {ci[1]:.4f}]")
        if validation.statistics.permutation_p_value is not None:
            print(f"  ✓ Permutation p-value: {validation.statistics.permutation_p_value:.4f}")
    print()

    # 4. Assemble evidence bundle
    print("[4/5] Assembling evidence bundle...")
    assembler = EvidenceAssembler()
    bundle = assembler.assemble(spec.model_dump(), trace, validation)
    print(f"  ✓ Bundle ID: {bundle.bundle_id}")
    print(f"  ✓ Evidence hash: {bundle.evidence_hash[:32]}...")
    print()

    # 5. Generate raw evidence report
    print("[5/5] Generating raw evidence report...")
    reporter = Reporter()
    report = reporter.generate_raw_evidence_report(trace, validation, bundle)

    # Save the report
    report_path = os.path.join(os.path.dirname(__file__), "poc_evidence_report.txt")
    with open(report_path, "w") as f:
        f.write(report)
    print(f"  ✓ Report saved: {report_path}")

    # Save the evidence bundle
    bundle_path = os.path.join(os.path.dirname(__file__), "poc_evidence_bundle.json")
    bundle.save(bundle_path)
    print(f"  ✓ Bundle saved: {bundle_path}")
    print()

    # Print the report
    print()
    print(report)


if __name__ == "__main__":
    main()
