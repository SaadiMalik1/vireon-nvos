"""Shared Experiment Schema and Loader for VIREON Contracts."""
from typing import Dict, Any, Optional, List
import yaml
from pydantic import BaseModel


class ExperimentSchema(BaseModel):
    """Base Pydantic schema for all YAML experiments."""
    id: str
    classification: Dict[str, str]
    system: Dict[str, Any]
    stimulus: Optional[Dict[str, Any]] = None
    perturbation: Optional[Dict[str, Any]] = None
    expected: Dict[str, Any]
    measurements: List[str]
    evidence: List[str]
    regulatory: Optional[Dict[str, Any]] = None


def load_experiment_from_yaml(filepath: str) -> Any:
    """Loads an experiment from a YAML file using vireon-lab factory if available, or raw schema."""
    with open(filepath, 'r') as f:
        data = yaml.safe_load(f)
    
    schema = ExperimentSchema(**data)
    
    try:
        from vireon_lab.experiments.schema import load_experiment_from_schema
        return load_experiment_from_schema(schema)
    except ImportError:
        return schema
