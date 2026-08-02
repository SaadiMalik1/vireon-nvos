import numpy as np
from typing import Dict, Any, List, Type

from vireon_core.contracts.plugin import IMethodPlugin, ScientificReadinessLevel, ScientificContract, PluginCapability
from vireon_core.contracts.base import IScientificObject, SignalType
from vireon_core.contracts.decoder import IDecoder, DecoderNotFittedError

class SklearnLDAPlugin(IMethodPlugin, IDecoder):
    """
    Tier 1 Reference Wrapper for Scikit-Learn's Linear Discriminant Analysis (LDA).
    SRL-2 indicates it is a trusted reference wrapper.
    """
    def __init__(self):
        super().__init__()
        self._fitted = False
        try:
            from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
            self._lda = LinearDiscriminantAnalysis()
        except ImportError:
            self._lda = None

    @property
    def plugin_id(self) -> str:
        return "method_decoding_sklearn_lda"
        
    @property
    def version(self) -> str:
        return "1.0.0"
        
    @property
    def dependencies(self) -> List[str]:
        return ["scikit-learn", "numpy"]
        
    @property
    def srl(self) -> ScientificReadinessLevel:
        return ScientificReadinessLevel.SRL_2
        
    @property
    def contract(self) -> ScientificContract:
        return ScientificContract(
            mathematical_assumptions=["Gaussian distributed classes", "Identical covariance matrices"],
            supported_modalities=[SignalType.EEG, SignalType.MEG, SignalType.EMG, SignalType.EOG],
            validation_papers=["Fisher, R. A. (1936). The use of multiple measurements in taxonomic problems..."],
            reference_implementations=["sklearn.discriminant_analysis.LinearDiscriminantAnalysis"],
            expected_numerical_tolerances={"precision": 1e-6},
            purpose="Linear classification of continuous features"
        )
        
    @property
    def capabilities(self) -> List[PluginCapability]:
        return []
        
    @property
    def inputs(self) -> List[Type[IScientificObject]]:
        return []
        
    @property
    def outputs(self) -> List[Type[IScientificObject]]:
        return []
        
    def initialize(self, config: Dict[str, Any]) -> None:
        pass
        
    def execute(self, inputs: Dict[str, IScientificObject]) -> Dict[str, IScientificObject]:
        if not self._lda:
            raise RuntimeError("scikit-learn is required for SklearnLDAPlugin")
        return {}
        
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        if not self._lda:
            raise RuntimeError("scikit-learn is required for SklearnLDAPlugin")
        self._lda.fit(X, y)
        self._fitted = True
        
    def predict(self, X: np.ndarray) -> np.ndarray:
        if not getattr(self, '_fitted', False):
            raise DecoderNotFittedError("Decoder must be fitted before predict.")
        if not self._lda:
            raise RuntimeError("scikit-learn is required for SklearnLDAPlugin")
        return self._lda.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if not getattr(self, '_fitted', False):
            raise DecoderNotFittedError("Decoder must be fitted before predict_proba.")
        if not self._lda:
            raise RuntimeError("scikit-learn is required for SklearnLDAPlugin")
        return self._lda.predict_proba(X)
