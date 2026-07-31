import numpy as np
from typing import Dict, Any, List, Type

from vireon_core.contracts.plugin import IMethodPlugin, ScientificReadinessLevel, ScientificContract, PluginCapability
from vireon_core.contracts.base import IScientificObject, SignalType, ISignal

class MNECSPPlugin(IMethodPlugin):
    """
    Tier 1 Reference Wrapper for MNE-Python's Common Spatial Patterns (CSP).
    SRL-2 indicates it is a trusted reference wrapper but not a native VIREON implementation.
    """
    def __init__(self, n_components: int = 4):
        self.n_components = n_components
        try:
            from mne.decoding import CSP
            self._mne_csp = CSP(n_components=n_components, reg=None, log=True, norm_trace=False)
        except ImportError:
            self._mne_csp = None

    @property
    def plugin_id(self) -> str:
        return "method_spatial_mne_csp"
        
    @property
    def version(self) -> str:
        return "1.0.0"
        
    @property
    def dependencies(self) -> List[str]:
        return ["mne", "numpy"]
        
    @property
    def srl(self) -> ScientificReadinessLevel:
        return ScientificReadinessLevel.SRL_2
        
    @property
    def contract(self) -> ScientificContract:
        return ScientificContract(
            mathematical_assumptions=["Covariance matrices are diagonalizable", "Classes have different spatial variances"],
            supported_modalities=[SignalType.EEG, SignalType.MEG],
            validation_papers=["Ramoser, H., Muller-Gerking, J., & Pfurtscheller, G. (2000). Optimal spatial filtering..."],
            reference_implementations=["mne.decoding.CSP"],
            expected_numerical_tolerances={"precision": 1e-6},
            purpose="Spatial feature extraction for binary classification"
        )
        
    @property
    def capabilities(self) -> List[PluginCapability]:
        return []
        
    @property
    def inputs(self) -> List[Type[IScientificObject]]:
        return [ISignal]
        
    @property
    def outputs(self) -> List[Type[IScientificObject]]:
        return [ISignal] # Outputs features, but wrapped as ISignal for compatibility
        
    def initialize(self, config: Dict[str, Any]) -> None:
        if "n_components" in config:
            self.n_components = config["n_components"]
            from mne.decoding import CSP
            self._mne_csp = CSP(n_components=self.n_components, reg=None, log=True, norm_trace=False)
        
    def execute(self, inputs: Dict[str, IScientificObject]) -> Dict[str, IScientificObject]:
        if not self._mne_csp:
            raise RuntimeError("MNE is required for MNECSPPlugin")
            
        # For a real pipeline, execute would take trials and labels, fit, and transform.
        # This is a stubbed representation for the architecture scaffolding.
        return {}
        
    def fit_transform(self, X: np.ndarray, y: np.ndarray) -> np.ndarray:
        if not self._mne_csp:
            raise RuntimeError("MNE is required for MNECSPPlugin")
        return self._mne_csp.fit_transform(X, y)
        
    def transform(self, X: np.ndarray) -> np.ndarray:
        if not self._mne_csp:
            raise RuntimeError("MNE is required for MNECSPPlugin")
        return self._mne_csp.transform(X)
