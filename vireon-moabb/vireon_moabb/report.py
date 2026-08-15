"""
Reporter — generates the raw evidence report (NO scorecard).

Key principle (ADR 0008 #9): No scorecard until underlying evidence is complete.
This reporter produces a raw evidence report that shows every artifact:
- What was executed
- What was validated
- What statistics were computed
- What provenance was captured
- The evidence hash

No "87/100" score. Just the facts, traceable to execution.
"""
from datetime import datetime, timezone
from vireon_moabb.executor import MoabbExecutionTrace
from vireon_moabb.validation import ValidationResult
from vireon_moabb.evidence import EvidenceBundle


class Reporter:
    """Generates a raw evidence report from execution traces and validation."""

    def generate_raw_evidence_report(
        self,
        trace: MoabbExecutionTrace,
        validation: ValidationResult,
        bundle: EvidenceBundle,
    ) -> str:
        """Generate the raw evidence report.

        This is NOT a scorecard. It's a traceable, fact-based report.
        Every number comes from the execution trace.
        """
        lines = []
        meta = trace.dataset_metadata
        stats = validation.statistics

        # Header
        lines.append("═" * 60)
        lines.append("  VIREON × MOABB — RAW EVIDENCE REPORT")
        lines.append("═" * 60)
        lines.append("")

        # Experiment
        lines.append("EXPERIMENT")
        lines.append("─" * 40)
        lines.append(f"  Name:           {trace.spec.get('name', '')}")
        lines.append(f"  Goal:           {trace.spec.get('goal', '')}")
        lines.append(f"  Mode:           {trace.spec.get('mode', '')}")
        lines.append(f"  Seed:           {trace.seed}")
        lines.append("")

        # Dataset
        lines.append("DATASET")
        lines.append("─" * 40)
        lines.append(f"  Dataset:        {meta.dataset_class}")
        lines.append(f"  Subjects:       {meta.n_subjects} ({meta.subject_list})")
        lines.append(f"  Sessions/subject: {meta.n_sessions_per_subject}")
        lines.append(f"  Trials/subject: {meta.n_trials_per_subject}")
        lines.append(f"  Channels:       {len(meta.channels)} (e.g., {meta.channels[:8]})")
        lines.append(f"  Sampling rate:  {meta.sfreq} Hz")
        lines.append(f"  Classes:        {meta.n_classes} ({meta.class_labels})")
        lines.append("")

        # Paradigm
        lines.append("PARADIGM")
        lines.append("─" * 40)
        lines.append(f"  Type:           {meta.paradigm_class}")
        lines.append(f"  Filter:         {meta.fmin}-{meta.fmax} Hz")
        lines.append("")

        # Evaluation
        lines.append("EVALUATION")
        lines.append("─" * 40)
        eval_class = trace.spec.get("evaluation", {}).get("evaluation_class", "Unknown")
        lines.append(f"  Type:           {eval_class}")
        lines.append(f"  Folds:          {len(trace.fold_results)}")
        lines.append("")

        # MOABB Result
        lines.append("MOABB RESULT")
        lines.append("─" * 40)
        lines.append(f"  Mean accuracy:  {trace.mean_accuracy:.4f}")
        per_subj = trace.per_subject_accuracy
        if per_subj:
            lines.append("  Per-subject:")
            for s, acc in sorted(per_subj.items()):
                lines.append(f"    Subject {s}: {acc:.4f}")
        lines.append("")

        # Validation
        lines.append("VALIDATION")
        lines.append("─" * 40)
        for check in validation.data_checks:
            mark = "✓" if check.passed else "✗"
            lines.append(f"  {mark} {check.name}: {check.value}")
        for check in validation.leakage_checks:
            mark = "✓" if check.passed else "✗"
            lines.append(f"  {mark} {check.name}: {check.value}")
        lines.append("")

        # Statistics
        if stats:
            lines.append("STATISTICS")
            lines.append("─" * 40)
            lines.append(f"  Mean accuracy:  {stats.mean_accuracy:.4f}")
            lines.append(f"  Std accuracy:   {stats.std_accuracy:.4f}")
            lines.append(f"  Chance level:   {stats.chance_level:.4f}")
            mark = "✓" if stats.chance_level_passed else "✗"
            lines.append(f"  {mark} Above chance: {stats.chance_level_passed}")
            if stats.subject_level_ci:
                lower, upper = stats.subject_level_ci
                lines.append(f"  Subject-level CI ({stats.ci_level*100:.0f}%): [{lower:.4f}, {upper:.4f}]")
                lines.append(f"    (bootstrapped over {stats.n_subjects} subjects, NOT trials)")
            if stats.permutation_p_value is not None:
                mark = "✓" if stats.permutation_significant else "✗"
                lines.append(f"  {mark} Permutation test: p={stats.permutation_p_value:.4f} "
                             f"({'significant' if stats.permutation_significant else 'not significant'} at α=0.05)")
                lines.append(f"    ({stats.n_permutations} permutations, unit=subject)")
            lines.append("")

        # Reproducibility
        lines.append("REPRODUCIBILITY")
        lines.append("─" * 40)
        for check in validation.reproducibility_checks:
            mark = "✓" if check.passed else "✗"
            lines.append(f"  {mark} {check.name}: {check.value}")
        lines.append("")

        # Environment
        env = trace.environment
        lines.append("ENVIRONMENT")
        lines.append("─" * 40)
        lines.append(f"  Python:         {env.python_version}")
        lines.append(f"  MOABB:          {env.moabb_version}")
        lines.append(f"  MNE:            {env.mne_version}")
        lines.append(f"  NumPy:          {env.numpy_version}")
        lines.append(f"  SciPy:          {env.scipy_version}")
        lines.append(f"  scikit-learn:   {env.sklearn_version}")
        lines.append(f"  pyRiemann:      {env.pyriemann_version}")
        lines.append(f"  Platform:       {env.platform}")
        lines.append("")

        # Execution timing
        lines.append("EXECUTION")
        lines.append("─" * 40)
        lines.append(f"  Started:        {trace.execution_started_at}")
        lines.append(f"  Finished:       {trace.execution_finished_at}")
        lines.append("")

        # Evidence
        lines.append("EVIDENCE")
        lines.append("─" * 40)
        lines.append(f"  Bundle ID:      {bundle.bundle_id}")
        lines.append(f"  Evidence hash:  {bundle.evidence_hash}")
        lines.append(f"  Created:        {bundle.created_at}")
        lines.append(f"  All checks passed: {validation.all_passed}")
        lines.append("")

        # Provenance statement
        lines.append("PROVENANCE STATEMENT")
        lines.append("─" * 40)
        lines.append("  Every claim in this report traces to an execution artifact.")
        lines.append("  The evidence hash is a SHA-256 over:")
        lines.append("    - experiment specification")
        lines.append("    - execution trace (dataset, partitions, results, environment)")
        lines.append("    - validation results (checks, statistics)")
        lines.append("    - summary")
        lines.append("  Changing any field changes the hash.")
        lines.append("")

        # Verification
        lines.append("VERIFICATION")
        lines.append("─" * 40)
        lines.append("  To verify this evidence:")
        lines.append(f"    1. Check the SHA-256 hash matches: {bundle.evidence_hash[:16]}...")
        lines.append("    2. Re-run the experiment with the same spec and seed")
        lines.append("    3. Compare the new hash to this one")
        lines.append("")

        lines.append("═" * 60)
        lines.append("  END OF RAW EVIDENCE REPORT")
        lines.append("═" * 60)

        return "\n".join(lines)

    def generate_scorecard(self, bundle: EvidenceBundle) -> str:
        """Generate formatted Algorithm Compliance Scorecard from an EvidenceBundle."""
        from vireon_moabb.scorecard import build_scorecard

        summary = bundle.summary
        stats = bundle.validation_results.get("statistics") or {}
        data_checks = bundle.validation_results.get("data_checks", [])
        repro_checks = bundle.validation_results.get("reproducibility_checks", [])

        mean_accuracy = summary.get("mean_accuracy", 0.0)
        chance_level = stats.get("chance_level", 0.5)
        chance_passed = stats.get("chance_level_passed", True)
        has_ci = bool(stats.get("subject_level_ci"))
        has_permutation = stats.get("permutation_p_value") is not None
        permutation_significant = bool(stats.get("permutation_significant", False))

        n_repro_passed = sum(1 for c in repro_checks if c.get("passed", False))
        n_repro_total = len(repro_checks) if repro_checks else 1

        n_data_passed = sum(1 for c in data_checks if c.get("passed", False))
        n_data_total = len(data_checks) if data_checks else 1

        verified = bundle.verify()

        card = build_scorecard(
            mean_accuracy=mean_accuracy,
            chance_level=chance_level,
            chance_passed=chance_passed,
            has_ci=has_ci,
            has_permutation=has_permutation,
            permutation_significant=permutation_significant,
            n_repro_checks_passed=n_repro_passed,
            n_repro_checks_total=n_repro_total,
            n_robustness_passed=0,
            n_robustness_total=0,
            n_data_checks_passed=n_data_passed,
            n_data_checks_total=n_data_total,
            evidence_verified=verified,
        )

        lines = [
            "═" * 60,
            "  Algorithm Compliance Scorecard",
            "═" * 60,
            f"  Total Score: {card.total}/100 ({card.confidence} Confidence)",
            "─" * 60,
        ]
        for d in card.dimensions:
            lines.append(f"  • {d.name:20s}: {d.score}/{d.max} ({d.explanation})")
        lines.append("═" * 60)
        return "\n".join(lines)
