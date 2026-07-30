from typing import Any, Dict
from vireon_lab.experiments.base import BaseExperiment, ExperimentSchema
from pydantic import model_validator

class NormalExperiment(BaseExperiment):
    """
    Baseline neurotech operations without perturbations.
    """
    pass

class FaultExperiment(BaseExperiment):
    """
    Simulates hardware or software failures.
    """
    def __init__(self, schema: ExperimentSchema):
        super().__init__(schema)
        if not self.schema.perturbation or "fault_type" not in self.schema.perturbation.get("parameters", {}):
             raise ValueError("Fault scenarios must specify a fault_type in perturbation parameters.")

class AttackExperiment(BaseExperiment):
    """
    Includes adversarial perturbations and threat levels.
    """
    def __init__(self, schema: ExperimentSchema):
        super().__init__(schema)
        if "threat_level" not in self.schema.classification:
             raise ValueError("Attack scenarios must specify a threat_level in classification.")

class AgencyExperiment(BaseExperiment):
    """
    Evaluating intention vs. action mapping.
    """
    def __init__(self, schema: ExperimentSchema):
        super().__init__(schema)
        if "intended_action" not in self.schema.stimulus:
             raise ValueError("Agency scenarios must specify an intended_action in stimulus.")

class LifecycleExperiment(BaseExperiment):
    """
    Long-running scenarios testing state transitions.
    """
    pass
