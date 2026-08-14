from abc import ABC, abstractmethod
from typing import Dict, Any, Type, List
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
    def __init__(self, plugin_id: str, violated_assumption: str, details: str, remediation: str):
        super().__init__(f"Plugin {plugin_id} violated {violated_assumption}: {details}. Remediation: {remediation}")
        self.plugin_id = plugin_id
        self.violated_assumption = violated_assumption
        self.details = details
        self.remediation = remediation

STATIONARITY_PVALUE_THRESHOLD = 0.05  # threshold for ADF stationarity test

class ContractValidator:
    @staticmethod
    def validate(plugin: 'IPlugin', inputs: dict) -> None:
        contract = getattr(plugin, 'contract', None)
        import numpy as np

        def iter_arrays(inps):
            if isinstance(inps, dict):
                for v in inps.values():
                    if hasattr(v, 'data') and isinstance(v.data, np.ndarray):
                        yield v.data
                    elif isinstance(v, np.ndarray):
                        yield v
                    elif isinstance(v, dict):
                        yield from iter_arrays(v)

        for arr in iter_arrays(inputs):
            if np.any(np.isnan(arr)):
                raise ScientificContractViolation(
                    plugin_id=plugin.plugin_id,
                    violated_assumption="No NaN values",
                    details="Signal contains NaN values",
                    remediation="Impute or remove NaN values before processing"
                )
            if np.any(np.isinf(arr)):
                raise ScientificContractViolation(
                    plugin_id=plugin.plugin_id,
                    violated_assumption="No Inf values",
                    details="Signal contains Inf values",
                    remediation="Clip or remove Inf values before processing"
                )

        if contract is None:
            return

        for cond in contract.failure_conditions:
            if "nperseg" in cond.lower() and hasattr(plugin, 'nperseg'):
                for arr in iter_arrays(inputs):
                    # For Welch PSD, shape is typically (n_epochs, n_channels, n_times) or (n_times,)
                    if arr.shape[-1] < plugin.nperseg:
                        raise ScientificContractViolation(
                            plugin_id=plugin.plugin_id,
                            violated_assumption="Signal length >= nperseg",
                            details=f"Signal length {arr.shape[-1]} is < {plugin.nperseg}",
                            remediation="Increase signal length or decrease nperseg"
                        )
                        
        requires_stationarity = any("stationar" in a.lower() for a in contract.mathematical_assumptions)
        if requires_stationarity:
            try:
                from statsmodels.tsa.stattools import adfuller
                has_statsmodels = True
            except ImportError:
                has_statsmodels = False

            for arr in iter_arrays(inputs):
                sig_1d = arr.ravel()
                if len(sig_1d) > 100000:
                    sig_1d = sig_1d[:100000]
                
                if has_statsmodels:
                    result = adfuller(sig_1d)
                    p_value = result[1]
                    if p_value > STATIONARITY_PVALUE_THRESHOLD:
                        raise ScientificContractViolation(
                            plugin_id=plugin.plugin_id,
                            violated_assumption="Stationarity",
                            details=f"ADF test failed (p={p_value} > {STATIONARITY_PVALUE_THRESHOLD})",
                            remediation="Detrend or difference the signal to achieve stationarity"
                        )
                else:
                    n2 = len(sig_1d) // 2
                    m1, m2 = np.mean(sig_1d[:n2]), np.mean(sig_1d[n2:])
                    if abs(m1 - m2) > np.std(sig_1d):
                        import logging
                        logging.warning("statsmodels unavailable. Simple stationarity check failed.")
                        raise ScientificContractViolation(
                            plugin_id=plugin.plugin_id,
                            violated_assumption="Stationarity",
                            details="Simple mean/variance check failed",
                            remediation="Detrend or difference the signal to achieve stationarity"
                        )

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
    def verify_checksum(self, dataset_path: str, expected_checksum: str = None) -> bool:
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
