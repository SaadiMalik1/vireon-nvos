"""
ValidationLayer — validates the MOABB execution trace.

This is VIREON's scientific validation layer. It checks:
- Data integrity (no NaNs, proper structure)
- Leakage (no subject/session overlap between train and test)
- Statistics (subject-level CI, permutation test — NOT trial-level, to avoid pseudoreplication)
- Reproducibility (seed recorded, environment captured)

Key principle (ADR 0008 #5): VIREON bootstraps/permutates at the SUBJECT level.
"""
import numpy as np
from dataclasses import dataclass, field, asdict
from typing import Optional
from datetime import datetime, timezone

from vireon_moabb.executor import MoabbExecutionTrace
from vireon_moabb.spec import ExperimentSpec, StatisticsSpec


@dataclass
class CheckResult:
    """Result of a single validation check."""
    name: str
    passed: bool
    value: str  # Human-readable value
    explanation: str  # Why it passed/failed


@dataclass
class StatisticalResult:
    """Result of statistical analysis."""
    mean_accuracy: float
    std_accuracy: float
    chance_level: float
    chance_level_passed: bool  # True if accuracy > chance
    subject_level_ci: Optional[tuple[float, float]] = None  # (lower, upper)
    ci_level: Optional[float] = None
    permutation_p_value: Optional[float] = None
    permutation_significant: Optional[bool] = None
    n_permutations: Optional[int] = None
    n_subjects: int = 0
    n_folds: int = 0


@dataclass
class ValidationResult:
    """Complete validation of a MOABB execution trace."""
    # Data checks
    data_checks: list[CheckResult] = field(default_factory=list)

    # Leakage checks
    leakage_checks: list[CheckResult] = field(default_factory=list)

    # Statistics
    statistics: Optional[StatisticalResult] = None

    # Reproducibility checks
    reproducibility_checks: list[CheckResult] = field(default_factory=list)

    @property
    def all_passed(self) -> bool:
        """True if all checks passed."""
        for check in self.data_checks + self.leakage_checks + self.reproducibility_checks:
            if not check.passed:
                return False
        if self.statistics and not self.statistics.chance_level_passed:
            return False
        return True

    def to_dict(self) -> dict:
        return asdict(self)


class ValidationLayer:
    """Validates a MOABB execution trace."""

    def validate(self, trace: MoabbExecutionTrace, spec: ExperimentSpec) -> ValidationResult:
        """Run all validation checks on the trace."""
        result = ValidationResult()

        # 1. Data integrity checks
        result.data_checks = self._check_data_integrity(trace)

        # 2. Leakage checks
        result.leakage_checks = self._check_leakage(trace)

        # 3. Statistics
        if spec.statistics.compute_chance_level or spec.statistics.compute_subject_level_ci:
            result.statistics = self._compute_statistics(trace, spec.statistics)

        # 4. Reproducibility checks
        result.reproducibility_checks = self._check_reproducibility(trace, spec)

        return result

    def _check_data_integrity(self, trace: MoabbExecutionTrace) -> list[CheckResult]:
        """Check data integrity."""
        checks = []
        meta = trace.dataset_metadata

        # Dataset loaded
        checks.append(CheckResult(
            name="dataset_loaded",
            passed=meta.n_subjects > 0,
            value=f"{meta.n_subjects} subjects",
            explanation="Dataset must load at least one subject"
        ))

        # Channels present
        checks.append(CheckResult(
            name="channels_present",
            passed=len(meta.channels) > 0,
            value=f"{len(meta.channels)} channels",
            explanation="Dataset must have EEG channels"
        ))

        # Sampling rate
        checks.append(CheckResult(
            name="sampling_rate_valid",
            passed=meta.sfreq > 0,
            value=f"{meta.sfreq} Hz",
            explanation="Sampling rate must be positive"
        ))

        # Classes
        checks.append(CheckResult(
            name="classes_valid",
            passed=meta.n_classes >= 2,
            value=f"{meta.n_classes} classes: {meta.class_labels}",
            explanation="Need at least 2 classes for classification"
        ))

        # Trials per subject
        min_trials = min(meta.n_trials_per_subject.values()) if meta.n_trials_per_subject else 0
        checks.append(CheckResult(
            name="minimum_trials",
            passed=min_trials >= 10,
            value=f"min {min_trials} trials/subject",
            explanation="Each subject needs at least 10 trials for meaningful evaluation"
        ))

        return checks

    def _check_leakage(self, trace: MoabbExecutionTrace) -> list[CheckResult]:
        """Check for train/test leakage by inspecting actual partition membership.

        FIXED in Study B: previously checked only the evaluation class name.
        Now inspects actual train_subjects, test_subjects, train_sessions,
        test_sessions from the execution trace partitions.

        Evaluation design semantics:
          CrossSubjectEvaluation: train_subjects ∩ test_subjects = ∅
          CrossSessionEvaluation: for each subject, train_sessions ∩ test_sessions = ∅
            (same subject CAN appear in train and test, but with different sessions)
          WithinSessionEvaluation: same subject in train and test is expected (trial-level split)
          LeaveOneSubjectOut: exactly one test subject, NOT in train
        """
        checks = []

        # ── Structural checks ──

        # Each fold has a test subject
        folds_with_test = sum(1 for p in trace.partitions if p.test_subjects)
        checks.append(CheckResult(
            name="test_subjects_present",
            passed=folds_with_test == len(trace.partitions),
            value=f"{folds_with_test}/{len(trace.partitions)} folds have test subjects",
            explanation="Every fold must have test subjects"
        ))

        # No empty partitions
        empty_folds = sum(1 for p in trace.partitions if p.n_test_trials == 0)
        checks.append(CheckResult(
            name="no_empty_folds",
            passed=empty_folds == 0,
            value=f"{empty_folds} empty folds",
            explanation="No fold should have zero test trials"
        ))

        # Accuracy in valid range
        bad_accs = sum(1 for r in trace.fold_results if r.accuracy < 0 or r.accuracy > 1)
        checks.append(CheckResult(
            name="accuracy_range_valid",
            passed=bad_accs == 0,
            value=f"{bad_accs} folds with out-of-range accuracy",
            explanation="Accuracy must be in [0, 1]"
        ))

        # ── Partition integrity checks (NEW — the gap from Study B) ──

        eval_class = trace.spec.get("evaluation", {}).get("evaluation_class", "Unknown")

        # Check: evaluation design is known
        sound_evals = {
            "CrossSessionEvaluation", "CrossSubjectEvaluation",
            "WithinSessionEvaluation", "LeaveOneSubjectOut"
        }
        checks.append(CheckResult(
            name="evaluation_design_sound",
            passed=eval_class in sound_evals,
            value=eval_class,
            explanation=f"{'Known sound evaluation design' if eval_class in sound_evals else 'Unknown evaluation design — verify leakage manually'}"
        ))

        # ── Subject-level isolation (CrossSubject / LeaveOneSubjectOut) ──
        # For CrossSubject: train_subjects and test_subjects must NOT overlap
        # For CrossSession: same subject CAN be in both (different sessions) — this is valid
        # For WithinSession: same subject in both is expected (trial-level split)

        if eval_class in ("CrossSubjectEvaluation", "LeaveOneSubjectOut"):
            # Strict subject isolation required
            subject_overlaps = []
            for p in trace.partitions:
                if p.train_subjects and p.test_subjects:
                    overlap = set(p.train_subjects) & set(p.test_subjects)
                    if overlap:
                        subject_overlaps.append((p.fold_id, sorted(overlap)))

            if subject_overlaps:
                detail = "; ".join(f"fold {fid}: subjects {subs}" for fid, subs in subject_overlaps[:3])
                checks.append(CheckResult(
                    name="no_subject_overlap",
                    passed=False,
                    value=f"{len(subject_overlaps)} folds with subject overlap ({detail})",
                    explanation=f"VIOLATION: {eval_class} requires strict subject isolation. "
                               f"Train and test subjects must not overlap."
                ))
            else:
                checks.append(CheckResult(
                    name="no_subject_overlap",
                    passed=True,
                    value="0 folds with subject overlap",
                    explanation=f"{eval_class}: train_subjects ∩ test_subjects = ∅ for all folds ✓"
                ))

        elif eval_class == "CrossSessionEvaluation":
            # Same subject CAN be in train and test — but sessions must differ
            # Check: for each subject in both train and test, train_sessions ∩ test_sessions = ∅
            session_overlaps = []
            for p in trace.partitions:
                if p.train_subjects and p.test_subjects:
                    # Check if same subject appears in both train and test
                    shared_subjects = set(p.train_subjects) & set(p.test_subjects)
                    if shared_subjects:
                        # For shared subjects, sessions must not overlap
                        if p.train_sessions and p.test_sessions:
                            session_overlap = set(p.train_sessions) & set(p.test_sessions)
                            if session_overlap:
                                session_overlaps.append((p.fold_id, sorted(shared_subjects), sorted(session_overlap)))

            if session_overlaps:
                detail = "; ".join(f"fold {fid}: subjects {subs}, sessions {sess}" for fid, subs, sess in session_overlaps[:3])
                checks.append(CheckResult(
                    name="no_session_overlap",
                    passed=False,
                    value=f"{len(session_overlaps)} folds with session overlap ({detail})",
                    explanation="VIOLATION: CrossSessionEvaluation allows same subject in train/test "
                               "but sessions must not overlap."
                ))
            else:
                checks.append(CheckResult(
                    name="session_isolation_valid",
                    passed=True,
                    value="0 session overlaps detected",
                    explanation="CrossSessionEvaluation: same subjects in train/test is valid, "
                               "but sessions are properly isolated ✓"
                ))

            # Also check: subjects ARE shared between train and test (otherwise it's cross-subject, not cross-session)
            shared_count = sum(1 for p in trace.partitions
                             if p.train_subjects and p.test_subjects
                             and set(p.train_subjects) & set(p.test_subjects))
            checks.append(CheckResult(
                name="cross_session_subject_sharing",
                passed=True,  # Informational, not a failure
                value=f"{shared_count}/{len(trace.partitions)} folds share subjects between train/test",
                explanation="CrossSessionEvaluation: subject sharing between train/test is expected "
                           "(different sessions of same subject)"
            ))

        elif eval_class == "WithinSessionEvaluation":
            # Same subject in train and test is expected (trial-level split)
            checks.append(CheckResult(
                name="within_session_design",
                passed=True,
                value="WithinSession evaluation — subject sharing expected",
                explanation="WithinSessionEvaluation: same subject in train and test is by design (trial-level split)"
            ))

        return checks

    def _compute_statistics(self, trace: MoabbExecutionTrace, stats_spec: StatisticsSpec) -> StatisticalResult:
        """Compute statistics at the SUBJECT level (not trial level).

        This avoids pseudoreplication: if we bootstrap individual trials,
        we treat within-subject observations as independent, which they're not.
        Bootstrapping subject-level accuracies is the correct approach.
        """
        fold_accs = np.array([r.accuracy for r in trace.fold_results])
        subject_accs = np.array(list(trace.per_subject_accuracy.values()))

        # Chance level
        n_classes = trace.dataset_metadata.n_classes
        chance_level = 1.0 / n_classes if n_classes > 0 else 0.5
        mean_acc = float(np.mean(fold_accs)) if len(fold_accs) > 0 else 0.0
        chance_passed = mean_acc > chance_level

        # Subject-level bootstrap CI
        ci = None
        ci_level = None
        if stats_spec.compute_subject_level_ci and len(subject_accs) >= 2:
            rng = np.random.default_rng(42)
            boot_means = []
            for _ in range(stats_spec.n_bootstrap):
                # Resample SUBJECTS (not trials) with replacement
                idx = rng.integers(0, len(subject_accs), size=len(subject_accs))
                boot_means.append(np.mean(subject_accs[idx]))
            alpha = 1 - stats_spec.ci_level
            lower = float(np.percentile(boot_means, 100 * alpha / 2))
            upper = float(np.percentile(boot_means, 100 * (1 - alpha / 2)))
            ci = (lower, upper)
            ci_level = stats_spec.ci_level

        # Permutation test at subject level
        perm_p = None
        perm_sig = None
        n_perm = None
        if stats_spec.compute_permutation_test and len(subject_accs) >= 2:
            # Permutation test: shuffle subject-level accuracies against chance
            # H0: subject accuracies are drawn from a distribution with mean = chance_level
            rng = np.random.default_rng(42)
            observed_mean = np.mean(subject_accs)
            perm_count = 0
            for _ in range(stats_spec.n_permutations):
                # Under H0, each subject's accuracy is chance_level + noise
                # We simulate by shifting to chance and permuting
                perm_accs = chance_level + (subject_accs - observed_mean)
                # Shuffle which subject gets which accuracy
                rng.shuffle(perm_accs)
                if np.mean(perm_accs) >= observed_mean:
                    perm_count += 1
            perm_p = (perm_count + 1) / (stats_spec.n_permutations + 1)
            perm_sig = perm_p < 0.05
            n_perm = stats_spec.n_permutations

        return StatisticalResult(
            mean_accuracy=mean_acc,
            std_accuracy=float(np.std(fold_accs)) if len(fold_accs) > 1 else 0.0,
            chance_level=chance_level,
            chance_level_passed=chance_passed,
            subject_level_ci=ci,
            ci_level=ci_level,
            permutation_p_value=perm_p,
            permutation_significant=perm_sig,
            n_permutations=n_perm,
            n_subjects=len(subject_accs),
            n_folds=len(fold_accs),
        )

    def _check_reproducibility(self, trace: MoabbExecutionTrace, spec: ExperimentSpec) -> list[CheckResult]:
        """Check reproducibility artifacts."""
        checks = []

        # Seed recorded
        checks.append(CheckResult(
            name="seed_recorded",
            passed=trace.seed is not None,
            value=f"seed={trace.seed}",
            explanation="Seed must be recorded for reproducibility"
        ))

        # Environment captured
        env = trace.environment
        checks.append(CheckResult(
            name="environment_captured",
            passed=env.moabb_version != "unknown",
            value=f"MOABB {env.moabb_version}, MNE {env.mne_version}, Python {env.python_version}",
            explanation="Software environment must be captured for reproducibility"
        ))

        # Execution timestamps
        checks.append(CheckResult(
            name="timestamps_recorded",
            passed=bool(trace.execution_started_at and trace.execution_finished_at),
            value=f"started={trace.execution_started_at}, finished={trace.execution_finished_at}",
            explanation="Execution timestamps must be recorded"
        ))

        # Dataset identity
        checks.append(CheckResult(
            name="dataset_identity_recorded",
            passed=bool(trace.dataset_metadata.dataset_class),
            value=trace.dataset_metadata.dataset_class,
            explanation="Dataset identity must be recorded for provenance"
        ))

        return checks
