from typing import Any
import yaml
import numpy as np

from vireon_core.contracts import IExperimentDef, IProvider
from vireon_lab.experiments.base import ExperimentSchema
from vireon_lab.experiments.types import NormalExperiment, FaultExperiment, AttackExperiment, AgencyExperiment, LifecycleExperiment

# A simple mock provider for testing
class MockProvider(IProvider):
    def start(self) -> None:
        pass
    def stop(self) -> None:
        pass
    def get_data(self) -> Any:
        return {"data": np.zeros((100, 2))}

def load_experiment_from_yaml(filepath: str) -> IExperimentDef:
    """
    Loads an experiment from a YAML file and returns the correct IExperimentDef subclass based on type.
    """
    with open(filepath, 'r') as f:
        data = yaml.safe_load(f)
    
    schema = ExperimentSchema(**data)
    
    # Factory logic based on classification.type
    s_type = schema.classification.get("type", "normal")
    
    if s_type == "normal":
        return NormalExperiment(schema)
    elif s_type == "fault":
        return FaultExperiment(schema)
    elif s_type == "attack" or s_type == "adversarial":
        return AttackExperiment(schema)
    elif s_type == "agency_integrity":
        return AgencyExperiment(schema)
    elif s_type == "lifecycle":
        return LifecycleExperiment(schema)
    else:
        # Default fallback
        return NormalExperiment(schema)
