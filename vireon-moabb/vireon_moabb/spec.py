from pydantic import BaseModel, Field
from typing import Any, Optional

class ProvenanceSpec(BaseModel):
    seed: int = 42

class DatasetMetadata(BaseModel):
    dataset_class: str
    n_subjects: int
    n_classes: int

class ParadigmSpec(BaseModel):
    paradigm_class: str
    fmin: float = 8.0
    fmax: float = 32.0

class EvaluationSpec(BaseModel):
    evaluation_class: str

class PerturbationSpec(BaseModel):
    type: str
    severity: float

class RobustnessSpec(BaseModel):
    perturbations: list[PerturbationSpec] = []

class ExperimentSpec(BaseModel):
    name: str = ""
    goal: str = ""
    mode: str = "standard"
    dataset: str
    subject: Optional[int] = None
    pipeline_name: str
    paradigm: ParadigmSpec = Field(default_factory=lambda: ParadigmSpec(paradigm_class="LeftRightImagery"))
    evaluation: EvaluationSpec = Field(default_factory=lambda: EvaluationSpec(evaluation_class="WithinSessionEvaluation"))
    provenance: ProvenanceSpec = Field(default_factory=ProvenanceSpec)
    robustness: Optional[RobustnessSpec] = None

def standard_spec(dataset: str, subject: Optional[int], pipeline_name: str, goal: str = "") -> ExperimentSpec:
    return ExperimentSpec(
        name=f"Standard {pipeline_name} on {dataset}",
        goal=goal,
        mode="standard",
        dataset=dataset,
        subject=subject,
        pipeline_name=pipeline_name
    )

def quick_spec(dataset: str, subject: int, pipeline_name: str) -> ExperimentSpec:
    spec = standard_spec(dataset, subject, pipeline_name)
    spec.mode = "quick"
    return spec

def research_spec(dataset: str, subject: Optional[int], pipeline_name: str) -> ExperimentSpec:
    spec = standard_spec(dataset, subject, pipeline_name)
    spec.mode = "research"
    return spec
