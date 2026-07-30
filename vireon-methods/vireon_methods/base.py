from abc import ABC, abstractmethod
from typing import List, Dict, Any, Type
import numpy as np
from vireon_core.contracts.plugin import IPlugin, ScientificContract, ScientificReadinessLevel, PluginCapability
from vireon_core.contracts.base import IScientificObject, ISignal, SignalType

class IMethodology(IPlugin, ABC):
    """
    Base class for verified methodologies, integrating into the capability-based kernel.
    """
    pass

class WelchPSD(IMethodology):
    """
    Verified implementation of Welch's Method for PSD estimation.
    """
    def __init__(self, nperseg: int = 256, noverlap: int = None):
        self.nperseg = nperseg
        self.noverlap = noverlap

    @property
    def plugin_id(self) -> str:
        return "vk:Method:Welch"
        
    @property
    def version(self) -> str:
        return "0.1.0"
        
    @property
    def srl(self) -> ScientificReadinessLevel:
        return ScientificReadinessLevel.SRL_3 # Verified against scipy reference implementation
        
    @property
    def contract(self) -> ScientificContract:
        return ScientificContract(
            purpose="Estimate Power Spectral Density (PSD) using Welch's method",
            mathematical_assumptions=[
                "vk:Assumption:Stationarity (Wide-Sense Stationary)", 
                "vk:Assumption:Ergodicity"
            ],
            numerical_assumptions=[
                "Windowing reduces spectral leakage but decreases resolution",
                "Segment averaging reduces variance by a factor of K"
            ],
            computational_assumptions=[
                "FFT is efficient (O(N log N))"
            ],
            supported_modalities=[SignalType.EEG, SignalType.ECOG, SignalType.SEEG, SignalType.LFP, SignalType.EMG],
            unsupported_modalities=[SignalType.SPIKE],
            failure_conditions=["Signal length < nperseg"],
            known_artifacts=["Spectral leakage", "Scalloping loss"],
            expected_uncertainty=["Variance decreases as 1/K where K is number of segments"],
            validation_papers=["10.1109/TAU.1967.1161901"],
            reference_implementations=["scipy.signal.welch"],
            reference_software=["SciPy"],
            expected_numerical_tolerances={"psd_error": 1e-10},
            calibration_provenance="Deterministic algorithm"
        )
        
    @property
    def capabilities(self) -> List[PluginCapability]:
        return [PluginCapability(
            id="spectral_estimation",
            version="0.1.0",
            consumes=["ISignal"],
            produces=["ISignal"],
            assumptions=["Signal has finite energy"],
            uncertainty_model=["Variance reduction proportional to number of segments"]
        )]
        
    @property
    def inputs(self) -> List[Type[IScientificObject]]:
        return [ISignal]
        
    @property
    def outputs(self) -> List[Type[IScientificObject]]:
        return [ISignal] # Outputting PSD conceptually as a signal over frequency
        
    def execute(self, inputs: Dict[str, IScientificObject]) -> Dict[str, IScientificObject]:
        signal = inputs.get("signal")
        if not isinstance(signal, ISignal):
            raise ValueError("Expected ISignal as 'signal' input")
            
        data = signal.data
        fs = signal.sampling_rate
        
        # Scientific Check: Data length vs nperseg
        if data.shape[0] < self.nperseg:
            raise ValueError("Signal length must be >= nperseg for Welch's method to be valid.")
            
        import scipy.signal
        f, Pxx = scipy.signal.welch(data, fs=fs, nperseg=self.nperseg, noverlap=self.noverlap, axis=0)
        
        return {"psd": ISignal(sampling_rate=1.0, data=Pxx)}
