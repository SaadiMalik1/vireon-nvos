from abc import ABC, abstractmethod
from typing import Dict, Any, Type, List, Optional
from pydantic import BaseModel
from enum import IntEnum
from vireon_core.contracts.base import IScientificObject, SignalType

class ScientificReadinessLevel(IntEnum):
    SRL_0 = 0  # Concept only
    SRL_1 = 1  # Mathematical implementation
    SRL_2 = 2  # Unit tested
    SRL_3 = 3  # Cross-validated against another tool
    SRL_4 = 4  # Verified on public datasets
    SRL_5 = 5  # Literature reproduced
    SRL_6 = 6  # Used in published research
    SRL_7 = 7  # Multi-laboratory validation
    SRL_8 = 8  # Clinical evaluation
    SRL_9 = 9  # Regulatory-grade evidence

class ScientificContract(BaseModel):
    mathematical_assumptions: List[str] = []
    computational_assumptions: List[str] = []
    numerical_assumptions: List[str] = []
    statistical_assumptions: List[str] = []
    hardware_assumptions: List[str] = []
    dataset_assumptions: List[str] = []
    regulatory_applicability: List[str] = []
    supported_modalities: List[SignalType] = []
    unsupported_modalities: List[SignalType] = []
    expected_uncertainty: List[str] = []
    failure_conditions: List[str] = []
    calibration_datasets: List[str] = []
    validation_datasets: List[str] = []
    purpose: str = ""
    known_artifacts: List[str] = []
    validation_papers: List[str] = []
    reference_implementations: List[str] = []
    reference_software: List[str] = []
    expected_numerical_tolerances: Dict[str, float] = {}
    calibration_provenance: str = ""

class PluginCapability(BaseModel):
    id: str
    version: str
    consumes: List[str]
    produces: List[str]
    assumptions: List[str]
    uncertainty_model: List[str]

class IPlugin(ABC):
    """
    Capability-based interface for all VIREON plugins.
    The kernel routes IScientificObjects based on capabilities.
    """
    @property
    @abstractmethod
    def plugin_id(self) -> str:
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        pass

    @property
    @abstractmethod
    def srl(self) -> ScientificReadinessLevel:
        """
        Returns the Scientific Readiness Level of the plugin.
        """
        pass

    @property
    @abstractmethod
    def contract(self) -> ScientificContract:
        """
        Explicitly declares the scientific contract constraints of the plugin.
        """
        pass

    @property
    @abstractmethod
    def capabilities(self) -> List[PluginCapability]:
        pass
        
    @property
    @abstractmethod
    def inputs(self) -> List[Type[IScientificObject]]:
        pass
        
    @property
    @abstractmethod
    def outputs(self) -> List[Type[IScientificObject]]:
        pass

    @abstractmethod
    def execute(self, inputs: Dict[str, IScientificObject]) -> Dict[str, IScientificObject]:
        pass
