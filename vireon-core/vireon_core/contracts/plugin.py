from abc import ABC, abstractmethod
from typing import Dict, Any, Type, List, Optional
from pydantic import BaseModel
from enum import IntEnum
from vireon_core.contracts.base import IScientificObject, SignalType

class ScientificReadinessLevel(IntEnum):
    SRL_0 = 0  # Unverified Idea
    SRL_1 = 1  # Mathematical Proof
    SRL_2 = 2  # Synthetic Validation
    SRL_3 = 3  # Numerical Equivalence
    SRL_4 = 4  # Adversarial Validation
    SRL_5 = 5  # Empirical Validation
    SRL_6 = 6  # Physiological Validation
    SRL_7 = 7  # Multi-Lab Reproducibility
    SRL_8 = 8  # Clinical Retrospective
    SRL_9 = 9  # Regulatory Grade

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
    capabilities_provided: List[str] = []

class ScientificContractViolation(Exception):
    """
    Raised when a plugin's execution violates its declared Scientific Contract
    (e.g., input data violates mathematical assumptions or numerical tolerances).
    """
    pass

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

    @property
    @abstractmethod
    def plugin_type(self) -> str:
        """
        Returns the specific type of plugin (e.g., 'method', 'hardware', 'artifact').
        """
        pass

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initializes the plugin with the given configuration.
        """
        pass

    @abstractmethod
    def execute(self, inputs: Dict[str, IScientificObject]) -> Dict[str, IScientificObject]:
        pass

class IDatasetPlugin(IPlugin):
    """
    Plugin interface for acquiring and formatting canonical validation datasets.
    """
    @abstractmethod
    def download(self, cache_dir: str) -> None:
        pass

    @abstractmethod
    def verify_checksum(self, cache_dir: str) -> bool:
        pass
        
    @abstractmethod
    def verify_license(self) -> bool:
        pass
        
    @abstractmethod
    def convert_to_bids(self, cache_dir: str, bids_dir: str) -> None:
        pass
        
    @abstractmethod
    def generate_metadata(self, bids_dir: str) -> Dict[str, Any]:
        pass
        
    @abstractmethod
    def generate_hash(self, bids_dir: str) -> str:
        pass
        
    @abstractmethod
    def create_manifest(self, output_path: str) -> None:
        pass

    @abstractmethod
    def load(self, subject_id: str, bids_root: str) -> IScientificObject:
        pass
        
    @abstractmethod
    def stream(self, subject_id: str, bids_root: str):
        pass
        
    @abstractmethod
    def iterate(self, bids_root: str):
        pass
        
    @abstractmethod
    def statistics(self, bids_root: str) -> Dict[str, Any]:
        pass
        
    @abstractmethod
    def quality_report(self, bids_root: str) -> Dict[str, Any]:
        pass

class IMethodPlugin(IPlugin):
    """
    Plugin interface for scientific methods (Signal Processing, ML, etc).
    """
    @property
    def plugin_type(self) -> str:
        return "method"
        
    @property
    @abstractmethod
    def dependencies(self) -> List[str]:
        pass
