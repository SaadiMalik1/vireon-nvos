from typing import Literal, Optional, Any
from pydantic import BaseModel, Field, model_validator


class DatasetSpec(BaseModel):
    source: str = Field(description="File path or dataset key (e.g., 'motor_imagery.edf' or 'physionet_bci')")
    subject: Optional[int] = Field(default=None, description="Subject ID (1-indexed)")
    runs: Optional[list[int]] = Field(default=None, description="Run IDs to load")
    format: Optional[str] = Field(default=None, description="Auto-detected if omitted: edf, fif, bids, etc.")
    fs: Optional[float] = Field(default=None, description="Sampling rate; auto-detected if omitted")
    channels: Optional[list[str]] = Field(default=None, description="Channel names; auto-detected if omitted")
    epoch_length: Optional[float] = Field(default=None, description="Epoch length in seconds (e.g., 2.0)")


class PreprocessingSpec(BaseModel):
    type: Literal["filter", "epoch", "reference", "artifact_rejection", "downsample"]
    parameters: dict[str, Any] = Field(default_factory=dict)


class MethodSpec(BaseModel):
    algorithm: str = Field(description="Plugin ID (e.g., 'vk:Method:CSP') or short name ('csp')")
    parameters: dict[str, Any] = Field(default_factory=dict)
    decoder: Optional[str] = Field(default=None, description="Decoder: 'lda', 'svm', 'logistic', None")
    decoder_params: dict[str, Any] = Field(default_factory=dict)


class ValidationSpec(BaseModel):
    strategy: Literal["train_test_split", "k_fold", "subject_wise", "leave_one_out", "single_run"]
    k: Optional[int] = Field(default=None, description="Number of folds (for k_fold, subject_wise)")
    test_size: Optional[float] = Field(default=None, description="Test fraction (for train_test_split)")
    random_state: int = Field(default=42)
    leakage_check: bool = Field(default=True, description="Verify no train/test contamination")


class StatisticsSpec(BaseModel):
    metrics: list[str] = Field(default=["accuracy"], description="accuracy, balanced_accuracy, cohen_kappa, auc, f1")
    significance_test: Optional[Literal["permutation", "t_test", "wilcoxon"]] = Field(default=None)
    n_permutations: int = Field(default=1000)
    confidence_interval: Optional[Literal["bootstrap", "wilson"]] = Field(default="bootstrap")
    ci_level: float = Field(default=0.95)
    n_bootstrap: int = Field(default=1000)


class PerturbationSpec(BaseModel):
    type: Literal["white_noise", "line_noise", "channel_dropout", "time_shift", "amplitude_scaling"]
    severity: float = Field(description="0.0 = none, 1.0 = severe")
    n_seeds: int = Field(default=5)


class RobustnessSpec(BaseModel):
    perturbations: list[PerturbationSpec] = Field(default_factory=list)


class ReferenceSpec(BaseModel):
    library: Literal["scipy", "mne", "sklearn", "analytical"]
    function: str = Field(description="e.g., 'scipy.signal.welch'")
    agreement_metric: Literal["ccc", "rmse", "pearson"] = Field(default="ccc")
    agreement_threshold: float = Field(default=0.99)


class ReportingSpec(BaseModel):
    format: Literal["text", "json", "html", "markdown"] = Field(default="text")
    verbosity: Literal["summary", "standard", "detailed"] = Field(default="standard")
    output_path: Optional[str] = Field(default=None)
    include_technical_details: bool = Field(default=False)


class ProvenanceSpec(BaseModel):
    record: bool = Field(default=True, description="Whether to record provenance at all")
    evidence_bundle: bool = Field(default=True, description="Cryptographic SHA-256 evidence bundle")
    environment_fingerprint: bool = Field(default=True)
    seed: int = Field(default=42)


class ExperimentSpec(BaseModel):
    """The architectural contract. Every interface constructs this; the engine executes this."""
    
    # Intent (for provenance and human-readable reports)
    name: str = Field(description="Human-readable experiment name")
    goal: str = Field(description="Natural-language intent. E.g., 'Determine whether CSP-LDA generalizes across subjects'")
    
    # Mode (determines defaults for unset fields)
    mode: Literal["quick", "standard", "research"] = Field(
        default="standard",
        description="Quick = minimal validation; Standard = CV+stats+CI; Research = full rigor"
    )
    
    # Pipeline stages
    dataset: DatasetSpec
    preprocessing: list[PreprocessingSpec] = Field(default_factory=list)
    method: MethodSpec
    validation: ValidationSpec
    statistics: StatisticsSpec = Field(default_factory=StatisticsSpec)
    robustness: Optional[RobustnessSpec] = Field(default=None, description="None = skip robustness testing")
    reference: Optional[ReferenceSpec] = Field(default=None, description="None = skip reference comparison")
    
    # Output
    reporting: ReportingSpec = Field(default_factory=ReportingSpec)
    provenance: ProvenanceSpec = Field(default_factory=ProvenanceSpec)
    
    @model_validator(mode="after")
    def validate_mode_consistency(self):
        """Mode implies certain defaults if user didn't set them explicitly."""
        if self.mode == "quick":
            if self.robustness is not None:
                raise ValueError("Quick mode does not support robustness testing. Use 'standard' or 'research' mode.")
            if self.reference is not None:
                raise ValueError("Quick mode does not support reference comparison. Use 'standard' or 'research' mode.")
        elif self.mode == "research":
            if self.robustness is None:
                raise ValueError("Research mode requires robustness testing. Set mode='standard' or provide robustness spec.")
        return self
    
    def to_yaml(self) -> str:
        import yaml
        return yaml.dump(self.model_dump(exclude_none=True), default_flow_style=False, sort_keys=False)
    
    @classmethod
    def from_yaml(cls, path: str) -> "ExperimentSpec":
        import yaml
        with open(path) as f:
            return cls.model_validate(yaml.safe_load(f))
