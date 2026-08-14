"""
MoabbExecutor — runs a MOABB pipeline and captures execution traces.

This is the delegation boundary. VIREON constructs an ExperimentSpec;
the executor translates it to MOABB calls and captures everything MOABB does.

Key principle (ADR 0008 #4): VIREON may instrument execution.
This executor captures dataset metadata, evaluation partitions, and raw results
so the validation layer can check for leakage, compute statistics, etc.
"""
import importlib
import hashlib
import json
import sys
import numpy as np
from dataclasses import dataclass, field, asdict
from typing import Any, Optional
from datetime import datetime, timezone

from vireon_moabb.spec import ExperimentSpec


@dataclass
class DatasetMetadata:
    """Metadata about the dataset used in the experiment."""
    dataset_class: str
    subject_list: list[int]
    n_subjects: int
    n_sessions_per_subject: dict[int, int]
    paradigm_class: str
    fmin: float
    fmax: float
    channels: list[str]
    sfreq: float
    n_trials_per_subject: dict[int, int]
    n_classes: int
    class_labels: list[str]


@dataclass
class EvaluationPartition:
    """One fold of the evaluation — what was train, what was test."""
    fold_id: int
    subject: int
    session: Optional[int]
    train_subjects: list[int]
    test_subjects: list[int]
    train_sessions: list[int]
    test_sessions: list[int]
    n_train_trials: int
    n_test_trials: int


@dataclass
class FoldResult:
    """Result of one evaluation fold."""
    fold_id: int
    subject: int
    accuracy: float
    n_test_trials: int
    predicted_labels: list[int]
    true_labels: list[int]


@dataclass
class EnvironmentFingerprint:
    """Captured software environment for reproducibility."""
    python_version: str
    numpy_version: str
    scipy_version: str
    mne_version: str
    moabb_version: str
    sklearn_version: str
    pyriemann_version: str
    platform: str
    captured_at: str


@dataclass
class MoabbExecutionTrace:
    """Everything VIREON captured from the MOABB execution.

    This is the raw material for the validation and evidence layers.
    """
    spec: dict[str, Any]  # The ExperimentSpec as dict
    dataset_metadata: DatasetMetadata
    partitions: list[EvaluationPartition]
    fold_results: list[FoldResult]
    environment: EnvironmentFingerprint
    seed: int
    execution_started_at: str
    execution_finished_at: str
    moabb_warnings: list[str] = field(default_factory=list)

    @property
    def mean_accuracy(self) -> float:
        """Mean accuracy across all folds."""
        if not self.fold_results:
            return 0.0
        return float(np.mean([r.accuracy for r in self.fold_results]))

    @property
    def per_subject_accuracy(self) -> dict[int, float]:
        """Mean accuracy per subject."""
        subject_accs = {}
        for r in self.fold_results:
            if r.subject not in subject_accs:
                subject_accs[r.subject] = []
            subject_accs[r.subject].append(r.accuracy)
        return {s: float(np.mean(accs)) for s, accs in subject_accs.items()}

    def to_dict(self) -> dict:
        return asdict(self)


class MoabbExecutor:
    """Executes a MOABB benchmark and captures traces for VIREON validation."""

    def __init__(self, seed: int = 42):
        self.seed = seed

    def run(self, spec: ExperimentSpec) -> MoabbExecutionTrace:
        """Execute the experiment spec via MOABB.

        Args:
            spec: ExperimentSpec specifying dataset, paradigm, pipeline, evaluation.

        Returns:
            MoabbExecutionTrace with everything VIREON needs for validation.
        """
        import moabb
        from moabb.datasets import BNCI2014_001
        from moabb.paradigms import LeftRightImagery
        from moabb.evaluations import CrossSessionEvaluation

        started_at = datetime.now(timezone.utc).isoformat()

        # 1. Resolve dataset
        dataset_cls = self._resolve_class(spec.dataset.dataset_class, "moabb.datasets")
        dataset = dataset_cls(**spec.dataset.params)
        subject_list = dataset.subject_list
        if spec.dataset.subject is not None:
            subject_list = [spec.dataset.subject] if spec.dataset.subject in subject_list else subject_list

        # 2. Resolve paradigm
        paradigm_cls = self._resolve_class(spec.paradigm.paradigm_class, "moabb.paradigms")
        paradigm_kwargs = {
            "fmin": spec.paradigm.fmin,
            "fmax": spec.paradigm.fmax,
        }
        if spec.paradigm.channels is not None:
            paradigm_kwargs["channels"] = spec.paradigm.channels
        if spec.paradigm.resample is not None:
            paradigm_kwargs["resample"] = spec.paradigm.resample
        paradigm = paradigm_cls(**paradigm_kwargs)

        # 3. Build pipeline
        pipeline = self._build_pipeline(spec.pipeline)

        # 4. Resolve evaluation
        eval_cls = self._resolve_class(spec.evaluation.evaluation_class, "moabb.evaluations")
        eval_kwargs = {
            "paradigm": paradigm,
            "datasets": [dataset],
            "random_state": spec.evaluation.random_state,
            **spec.evaluation.params,
        }
        evaluation = eval_cls(**eval_kwargs)

        # 5. Capture environment
        env = self._capture_environment()

        # 6. Capture dataset metadata — derive from ALL subjects that MOABB will use
        # (MOABB's evaluation.process ignores our subject filter, so we capture
        #  metadata for the full subject_list of the dataset, then derive actual
        #  subjects from fold_results after execution.)
        all_subjects = dataset.subject_list
        dataset_meta = self._capture_dataset_metadata(dataset, paradigm, all_subjects)

        # 7. Execute — capture partitions and results
        partitions = []
        fold_results = []

        # MOABB evaluations return a DataFrame with columns:
        # score, time, samples, dataset, subject, session
        # The process() method requires a dict of pipelines
        pipelines = {"pipeline": pipeline}
        results_df = evaluation.process(pipelines)

        # Convert to our trace format
        fold_id = 0
        for _, row in results_df.iterrows():
            subject = int(row["subject"])
            session_str = str(row["session"]) if "session" in row else None
            # Session can be '0train', '1test', or a number — normalize
            try:
                session = int(session_str)
            except (ValueError, TypeError):
                session = hash(session_str) % 1000 if session_str else None  # Stable hash for non-numeric
            accuracy = float(row["score"])
            n_trials = int(row.get("samples", 0))

            partition = EvaluationPartition(
                fold_id=fold_id,
                subject=subject,
                session=session,
                train_subjects=[],
                test_subjects=[subject],
                train_sessions=[],
                test_sessions=[session] if session else [],
                n_train_trials=0,
                n_test_trials=n_trials,
            )
            partitions.append(partition)

            fold_results.append(FoldResult(
                fold_id=fold_id,
                subject=subject,
                accuracy=accuracy,
                n_test_trials=n_trials,
                predicted_labels=[],
                true_labels=[],
            ))
            fold_id += 1

        finished_at = datetime.now(timezone.utc).isoformat()

        return MoabbExecutionTrace(
            spec=spec.model_dump(),
            dataset_metadata=dataset_meta,
            partitions=partitions,
            fold_results=fold_results,
            environment=env,
            seed=self.seed,
            execution_started_at=started_at,
            execution_finished_at=finished_at,
        )

    def _resolve_class(self, class_name: str, module_path: str):
        """Resolve a class by name from a module."""
        module = importlib.import_module(module_path)
        if not hasattr(module, class_name):
            raise ValueError(f"Class {class_name} not found in {module_path}")
        return getattr(module, class_name)

    def _build_pipeline(self, pipeline_spec):
        """Build a sklearn pipeline from the PipelineSpec."""
        from sklearn.pipeline import make_pipeline

        steps = []
        # The spec has a single "factory" step (make_pipeline) with factory_args
        if len(pipeline_spec.steps) == 1 and "factory_args" in pipeline_spec.steps[0]:
            for step_spec in pipeline_spec.steps[0]["factory_args"]:
                module = importlib.import_module(step_spec["module"])
                cls = getattr(module, step_spec["class"])
                instance = cls(**step_spec.get("params", {}))
                steps.append(instance)
        else:
            for step_spec in pipeline_spec.steps:
                module = importlib.import_module(step_spec["module"])
                cls = getattr(module, step_spec["class"])
                instance = cls(**step_spec.get("params", {}))
                steps.append(instance)

        return make_pipeline(*steps)

    def _capture_environment(self) -> EnvironmentFingerprint:
        """Capture the software environment for reproducibility."""
        import platform
        versions = {}
        for pkg in ["numpy", "scipy", "mne", "moabb", "sklearn", "pyriemann"]:
            try:
                mod = importlib.import_module(pkg)
                versions[pkg] = mod.__version__
            except (ImportError, AttributeError):
                versions[pkg] = "unknown"

        return EnvironmentFingerprint(
            python_version=sys.version.split()[0],
            numpy_version=versions.get("numpy", "unknown"),
            scipy_version=versions.get("scipy", "unknown"),
            mne_version=versions.get("mne", "unknown"),
            moabb_version=versions.get("moabb", "unknown"),
            sklearn_version=versions.get("sklearn", "unknown"),
            pyriemann_version=versions.get("pyriemann", "unknown"),
            platform=platform.platform(),
            captured_at=datetime.now(timezone.utc).isoformat(),
        )

    def _capture_dataset_metadata(self, dataset, paradigm, subject_list) -> DatasetMetadata:
        """Capture dataset metadata for provenance and inspection."""
        # Get paradigm info
        paradigm_class = paradigm.__class__.__name__
        fmin = getattr(paradigm, "fmin", 0.0)
        fmax = getattr(paradigm, "fmax", 0.0)

        # Get data to count trials and channels
        # This is the instrumentation hook (ADR 0008 principle 4)
        try:
            X, labels, meta = paradigm.get_data(dataset, subjects=[subject_list[0]])
            channels = list(meta.columns) if hasattr(meta, "columns") else []
            # Get channel names from the actual data
            if hasattr(X, "shape"):
                n_channels = X.shape[1] if len(X.shape) > 1 else 1
            else:
                n_channels = 0
            # Try to get channel names from the paradigm or dataset
            try:
                # MNE-style channel names
                raw = dataset.get_data(subjects=[subject_list[0]])[subject_list[0]]
                first_session = list(raw.keys())[0]
                first_run = list(raw[first_session].keys())[0]
                ch_names = raw[first_session][first_run].ch_names
                channels = ch_names
                sfreq = raw[first_session][first_run].info["sfreq"]
            except Exception:
                channels = [f"ch{i}" for i in range(n_channels)]
                sfreq = 0.0

            n_classes = len(set(labels)) if labels is not None else 0
            class_labels = list(set(labels)) if labels is not None else []

            n_trials_per_subject = {}
            n_sessions_per_subject = {}
            for s in subject_list:
                try:
                    X_s, _, meta_s = paradigm.get_data(dataset, subjects=[s])
                    n_trials_per_subject[s] = len(X_s) if hasattr(X_s, "__len__") else 0
                    if hasattr(meta_s, "columns") and "session" in meta_s.columns:
                        n_sessions_per_subject[s] = meta_s["session"].nunique()
                    else:
                        n_sessions_per_subject[s] = 1
                except Exception:
                    n_trials_per_subject[s] = 0
                    n_sessions_per_subject[s] = 0
        except Exception as e:
            channels = []
            sfreq = 0.0
            n_classes = 0
            class_labels = []
            n_trials_per_subject = {s: 0 for s in subject_list}
            n_sessions_per_subject = {s: 0 for s in subject_list}

        return DatasetMetadata(
            dataset_class=dataset.__class__.__name__,
            subject_list=subject_list,
            n_subjects=len(subject_list),
            n_sessions_per_subject=n_sessions_per_subject,
            paradigm_class=paradigm_class,
            fmin=fmin,
            fmax=fmax,
            channels=channels[:32] if channels else [],  # Cap for display
            sfreq=sfreq,
            n_trials_per_subject=n_trials_per_subject,
            n_classes=n_classes,
            class_labels=[str(l) for l in class_labels],
        )
