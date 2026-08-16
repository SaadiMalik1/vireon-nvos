"""
ExperimentSpec — the architectural contract between VIREON and MOABB.

This is a thin wrapper that specifies:
- MOABB delegation fields (dataset, paradigm, pipeline, evaluation)
- VIREON-owned validation fields (statistics, robustness, provenance)

See ADR 0008 for the principles.
"""
from typing import Literal, Optional, Any
from pydantic import BaseModel, Field
from dataclasses import dataclass


# ─── MOABB delegation specs ───

class DatasetSpec(BaseModel):
    """Which MOABB dataset to use."""
    dataset_class: str = Field(description="MOABB dataset class name, e.g., 'BNCI2014_001'")
    subject: Optional[int] = Field(default=None, description="Subject ID; None = all subjects")
    sessions: Optional[list[int]] = Field(default=None, description="Session IDs; None = all")
    # Constructor params for datasets that need them (e.g., FakeDataset)
    params: dict[str, Any] = Field(default_factory=dict)


class ParadigmSpec(BaseModel):
    """Which MOABB paradigm to use."""
    paradigm_class: str = Field(default="LeftRightImagery", description="MOABB paradigm class, e.g., 'LeftRightImagery'")
    fmin: float = Field(default=8.0, description="High-pass filter cutoff (Hz)")
    fmax: float = Field(default=32.0, description="Low-pass filter cutoff (Hz)")
    channels: Optional[list[str]] = Field(default=None, description="Channel list; None = all")
    resample: Optional[float] = Field(default=None, description="Resample rate (Hz); None = no resample")
    n_classes: Optional[int] = Field(default=None, description="Number of classes (for SSVEP, etc.)")


class PipelineSpec(BaseModel):
    """Which pipeline to evaluate.

    Specified as a list of steps, each a (module, class, params) tuple.
    This is serializable and reproducible.
    """
    steps: list[dict] = Field(description="List of {module, class, params} dicts")
    # Example:
    #   [
    #     {"module": "pyriemann.estimation", "class": "Covariances", "params": {"estimator": "oas"}},
    #     {"module": "pyriemann.tangentspace", "class": "TangentSpace", "params": {}},
    #     {"module": "sklearn.linear_model", "class": "LogisticRegression", "params": {"max_iter": 1000}},
    #   ]


class EvaluationSpec(BaseModel):
    """Which MOABB evaluation to use."""
    evaluation_class: str = Field(description="MOABB evaluation class, e.g., 'CrossSessionEvaluation'")
    random_state: int = Field(default=42)
    # Additional params passed to the evaluation constructor
    params: dict[str, Any] = Field(default_factory=dict)


# ─── VIREON-owned validation specs ───

class StatisticsSpec(BaseModel):
    """What statistics to compute.

    IMPORTANT: VIREON bootstraps/permutates at the SUBJECT level, not trial level.
    This avoids pseudoreplication when subjects contribute many trials.
    """
    compute_chance_level: bool = Field(default=True, description="Compute chance-level accuracy")
    compute_subject_level_ci: bool = Field(default=True, description="Bootstrap CI on subject-level accuracies")
    n_bootstrap: int = Field(default=1000)
    ci_level: float = Field(default=0.95)
    compute_permutation_test: bool = Field(default=True, description="Permutation test for significance")
    n_permutations: int = Field(default=1000)
    permutation_unit: Literal["subject", "session", "trial"] = Field(
        default="subject",
        description="What to shuffle. 'subject' = shuffle subject labels (most conservative)."
    )


class PerturbationSpec(BaseModel):
    """A single robustness perturbation."""
    name: str
    type: Literal["channel_dropout", "white_noise", "line_noise"]
    severity: float = Field(description="0.0 = none, 1.0 = severe")
    n_subjects: Optional[int] = Field(default=None, description="If set, only perturb this many subjects")


class RobustnessSpec(BaseModel):
    """What robustness tests to run."""
    perturbations: list[PerturbationSpec] = Field(default_factory=list)


class ProvenanceSpec(BaseModel):
    """What provenance to record."""
    record: bool = Field(default=True)
    capture_environment: bool = Field(default=True, description="Capture Python/numpy/scipy/mne/moabb versions")
    capture_seed: bool = Field(default=True)
    create_evidence_bundle: bool = Field(default=True, description="Create SHA-256 EvidenceBundle")
    seed: int = Field(default=42)


# ─── The contract ───

class ExperimentSpec(BaseModel):
    """The architectural contract. VIREON constructs this; MOABB executes the BCI part."""

    # Intent (VIREON-only, for provenance and human-readable reports)
    name: str = Field(description="Human-readable experiment name")
    goal: str = Field(description="Natural-language intent")

    mode: Literal["quick", "standard", "research"] = Field(
        default="standard",
        description="Quick = minimal validation; Standard = + statistics; Research = + robustness + evidence"
    )

    # MOABB delegation
    dataset: DatasetSpec
    paradigm: ParadigmSpec
    pipeline: PipelineSpec
    evaluation: EvaluationSpec

    # VIREON-owned validation
    statistics: StatisticsSpec = Field(default_factory=StatisticsSpec)
    robustness: Optional[RobustnessSpec] = Field(default=None)
    provenance: ProvenanceSpec = Field(default_factory=ProvenanceSpec)

    def to_yaml(self) -> str:
        import yaml
        return yaml.dump(self.model_dump(exclude_none=True), default_flow_style=False, sort_keys=False)


# ─── Presets ───

def quick_spec(dataset: str = "BNCI2014_001", subject: int = 1,
               pipeline_name: str = "logvar_lda", goal: str = "") -> ExperimentSpec:
    """Quick mode: single subject, minimal statistics, no robustness, no evidence bundle."""
    return ExperimentSpec(
        name=f"Quick validation: {pipeline_name} on {dataset}",
        goal=goal or f"Quick benchmark of {pipeline_name} on {dataset}",
        mode="quick",
        dataset=DatasetSpec(dataset_class=dataset, subject=subject),
        paradigm=ParadigmSpec(),
        pipeline=_get_pipeline(pipeline_name),
        evaluation=EvaluationSpec(evaluation_class="WithinSessionEvaluation"),
        statistics=StatisticsSpec(
            compute_chance_level=True,
            compute_subject_level_ci=False,
            compute_permutation_test=False,
        ),
        robustness=None,
        provenance=ProvenanceSpec(record=True, capture_environment=True, create_evidence_bundle=False),
    )


def standard_spec(dataset: str = "BNCI2014_001", subject: int = None,
                  pipeline_name: str = "logvar_lda", goal: str = "") -> ExperimentSpec:
    """Standard mode: all subjects, subject-level CI, permutation test."""
    return ExperimentSpec(
        name=f"Standard validation: {pipeline_name} on {dataset}",
        goal=goal or f"Standard validation of {pipeline_name} on {dataset}",
        mode="standard",
        dataset=DatasetSpec(dataset_class=dataset, subject=subject),
        paradigm=ParadigmSpec(),
        pipeline=_get_pipeline(pipeline_name),
        evaluation=EvaluationSpec(evaluation_class="CrossSessionEvaluation"),
        statistics=StatisticsSpec(
            compute_chance_level=True,
            compute_subject_level_ci=True,
            compute_permutation_test=True,
        ),
        robustness=None,
        provenance=ProvenanceSpec(record=True, capture_environment=True, create_evidence_bundle=True),
    )


def research_spec(dataset: str = "BNCI2014_001", subject: int = None,
                  pipeline_name: str = "logvar_lda", goal: str = "") -> ExperimentSpec:
    """Research mode: everything — statistics + robustness + evidence bundle."""
    return ExperimentSpec(
        name=f"Research validation: {pipeline_name} on {dataset}",
        goal=goal or f"Full scientific validation of {pipeline_name} on {dataset}",
        mode="research",
        dataset=DatasetSpec(dataset_class=dataset, subject=subject),
        paradigm=ParadigmSpec(),
        pipeline=_get_pipeline(pipeline_name),
        evaluation=EvaluationSpec(evaluation_class="CrossSessionEvaluation"),
        statistics=StatisticsSpec(
            compute_chance_level=True,
            compute_subject_level_ci=True,
            compute_permutation_test=True,
            n_permutations=1000,
        ),
        robustness=RobustnessSpec(perturbations=[
            PerturbationSpec(name="channel_dropout_20", type="channel_dropout", severity=0.2),
            PerturbationSpec(name="white_noise_0.1", type="white_noise", severity=0.1),
            PerturbationSpec(name="line_noise_50hz", type="line_noise", severity=0.5),
        ]),
        provenance=ProvenanceSpec(record=True, capture_environment=True, create_evidence_bundle=True),
    )


def _get_pipeline(name: str) -> PipelineSpec:
    """Get a pipeline spec by short name."""
    pipelines = {
        "logvar_lda": PipelineSpec(steps=[
            {"module": "moabb.pipelines", "class": "make_pipeline", "params": {}, "factory_args": [
                {"module": "moabb.pipelines.features", "class": "LogVariance", "params": {}},
                {"module": "sklearn.discriminant_analysis", "class": "LinearDiscriminantAnalysis", "params": {}},
            ]},
        ]),
        "csp_lda": PipelineSpec(steps=[
            {"module": "moabb.pipelines", "class": "make_pipeline", "params": {}, "factory_args": [
                {"module": "mne.decoding", "class": "CSP", "params": {"n_components": 8}},
                {"module": "sklearn.discriminant_analysis", "class": "LinearDiscriminantAnalysis", "params": {}},
            ]},
        ]),
        "riemann_lr": PipelineSpec(steps=[
            {"module": "moabb.pipelines", "class": "make_pipeline", "params": {}, "factory_args": [
                {"module": "pyriemann.estimation", "class": "Covariances", "params": {"estimator": "oas"}},
                {"module": "pyriemann.tangentspace", "class": "TangentSpace", "params": {}},
                {"module": "sklearn.linear_model", "class": "LogisticRegression", "params": {"max_iter": 1000}},
            ]},
        ]),
    }
    if name not in pipelines:
        raise ValueError(f"Unknown pipeline '{name}'. Available: {list(pipelines.keys())}")
    return pipelines[name]
