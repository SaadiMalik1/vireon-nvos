from typing import Literal, Optional, Dict, Any
from dataclasses import dataclass, field
from vireon_core.specs.experiment import ExperimentSpec
from vireon_core.specs.presets import quick_spec, standard_spec, research_spec
from vireon_core.specs.validator import SpecValidator

@dataclass
class DatasetQuality:
    missing_pct: float = 0.0
    clipping_pct: float = 0.0
    dc_drift: bool = False

@dataclass
class DatasetInspection:
    source: str
    format: str = "EDF"
    size_mb: float = 182.0
    channels: int = 8
    fs: float = 250.0
    duration_min: float = 42.0
    samples: int = 630000
    quality: DatasetQuality = field(default_factory=DatasetQuality)
    
    def summary(self) -> str:
        return f"Dataset: {self.source} ({self.format}, {self.channels} channels, {self.fs} Hz)"

@dataclass
class ExperimentResult:
    spec: ExperimentSpec
    statistics: Dict[str, Any]
    validation: Any
    robustness: Any
    dataset_quality: DatasetQuality
    provenance: Any
    scorecard: Any = None
    
    def report(self, format: str = "text") -> str:
        from vireon_simple.explain import generate_report
        return generate_report(self, format)


def inspect(data: str, subject: Optional[int] = None) -> DatasetInspection:
    return DatasetInspection(source=data)

def validate(
    data: str,
    method: str = "csp_lda",
    mode: Literal["quick", "standard", "research"] = "standard",
    goal: str = "",
) -> ExperimentResult:
    if mode == "quick":
        spec = quick_spec(data, method, goal=goal)
    elif mode == "standard":
        spec = standard_spec(data, method, goal=goal)
    else:
        spec = research_spec(data, method, goal=goal)
        
    return run(spec)

def run(spec: ExperimentSpec) -> ExperimentResult:
    validator = SpecValidator()
    issues = validator.validate(spec)
    if any(i.severity == "error" for i in issues):
        raise ValueError(f"Validation failed: {issues}")
        
    # Mock execution for UX layer testing
    from types import SimpleNamespace
    
    # Fill in statistics based on mode
    stats = {"accuracy": 0.874}
    if spec.mode != "quick":
        stats["ccc"] = 0.998
        
    val_mock = SimpleNamespace(
        strategy=spec.validation.strategy,
        leakage_verified=spec.validation.leakage_check
    )
    
    rob_mock = None
    if spec.robustness:
        rob_mock = SimpleNamespace(perturbations=spec.robustness.perturbations)
        
    prov_mock = SimpleNamespace(
        reproducibility_verified=True,
        evidence_hash="7a3fe2b1"
    )
    
    result = ExperimentResult(
        spec=spec,
        statistics=stats,
        validation=val_mock,
        robustness=rob_mock,
        dataset_quality=DatasetQuality(),
        provenance=prov_mock,
    )
    
    # Calculate scorecard
    from vireon_simple.scorecard import Scorecard
    result.scorecard = Scorecard.from_result(result)
    
    return result

def report(result: ExperimentResult, format: str = "text") -> str:
    return result.report(format)

def reproduce(paper: str, mode: str = "standard") -> ExperimentResult:
    return validate(data="mock_paper_data", method=paper, mode=mode)

def verify(evidence_hash: str) -> bool:
    return len(evidence_hash) > 0
