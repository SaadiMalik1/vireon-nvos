from dataclasses import dataclass
from typing import Literal, List
from vireon_core.specs.experiment import ExperimentSpec

@dataclass
class ValidationIssue:
    severity: Literal["error", "warning"]
    message: str

class SpecValidator:
    def validate(self, spec: ExperimentSpec) -> List[ValidationIssue]:
        issues = []
        
        # Validate dataset
        if not spec.dataset.source:
            issues.append(ValidationIssue("error", "Dataset source cannot be empty."))
            
        # Validate mode and validation strategy
        if spec.mode == "quick":
            if spec.validation.strategy != "single_run":
                issues.append(ValidationIssue("error", f"Validation strategy '{spec.validation.strategy}' is not allowed in 'quick' mode. Must be 'single_run'."))
                
        # Validate perturbation severity
        if spec.robustness:
            for p in spec.robustness.perturbations:
                if not (0.0 <= p.severity <= 1.0):
                    issues.append(ValidationIssue("error", f"Perturbation severity must be between 0.0 and 1.0, got {p.severity}."))
                    
        # Validate reference library
        if spec.reference:
            if spec.reference.library not in ["scipy", "mne", "sklearn", "analytical"]:
                issues.append(ValidationIssue("error", f"Reference library '{spec.reference.library}' is not supported."))
        
        return issues
