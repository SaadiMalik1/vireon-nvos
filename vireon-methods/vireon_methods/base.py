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

class FastICAMethod(IMethodology):
    """
    Verified implementation of FastICA for source separation.
    """
    def __init__(self, n_components: int = None, max_iter: int = 200, random_state: int = 42):
        self.n_components = n_components
        self.max_iter = max_iter
        self.random_state = random_state

    @property
    def plugin_id(self) -> str:
        return "vk:Method:ICA"
        
    @property
    def version(self) -> str:
        return "0.1.0"
        
    @property
    def srl(self) -> ScientificReadinessLevel:
        return ScientificReadinessLevel.SRL_3
        
    @property
    def contract(self) -> ScientificContract:
        return ScientificContract(
            purpose="Separate mixed signals into independent components using FastICA",
            mathematical_assumptions=[
                "vk:Assumption:StatisticalIndependence", 
                "vk:Assumption:NonGaussianity"
            ],
            numerical_assumptions=[
                "Whiten data before separation",
                "Fast convergence using Newton-Raphson"
            ],
            computational_assumptions=[
                "Max iterations limit convergence"
            ],
            supported_modalities=[SignalType.EEG, SignalType.ECOG, SignalType.SEEG, SignalType.MEG],
            unsupported_modalities=[],
            failure_conditions=["Gaussian sources cannot be separated"],
            known_artifacts=["Sign and variance ambiguity of components"],
            expected_uncertainty=["Local minima in optimization"],
            validation_papers=["10.1109/72.761722"],
            reference_implementations=["sklearn.decomposition.FastICA"],
            reference_software=["scikit-learn"],
            expected_numerical_tolerances={"reconstruction_error": 1e-5},
            calibration_provenance="Deterministic numerical algorithm"
        )
        
    @property
    def capabilities(self) -> List[PluginCapability]:
        return [PluginCapability(
            id="source_separation",
            version="0.1.0",
            consumes=["ISignal"],
            produces=["ISignal", "mixing_matrix"],
            assumptions=["Linear mixing"],
            uncertainty_model=["Convergence depends on random state"]
        )]
        
    @property
    def inputs(self) -> List[Type[IScientificObject]]:
        return [ISignal]
        
    @property
    def outputs(self) -> List[Type[IScientificObject]]:
        return [ISignal]
        
    def execute(self, inputs: Dict[str, IScientificObject]) -> Dict[str, IScientificObject]:
        signal = inputs.get("signal")
        if not isinstance(signal, ISignal):
            raise ValueError("Expected ISignal as 'signal' input")
            
        data = signal.data
        fs = signal.sampling_rate
        
        from sklearn.decomposition import FastICA
        ica = FastICA(n_components=self.n_components, max_iter=self.max_iter, random_state=self.random_state)
        sources = ica.fit_transform(data)
        
        return {"components": ISignal(sampling_rate=fs, data=sources)}

class ContinuousWaveletTransform(IMethodology):
    """
    Continuous Wavelet Transform (CWT) using Morlet wavelet.
    """
    def __init__(self, freqs: np.ndarray = np.arange(1, 50)):
        self.freqs = freqs

    @property
    def plugin_id(self) -> str:
        return "vk:Method:Wavelets"
        
    @property
    def version(self) -> str:
        return "0.1.0"
        
    @property
    def srl(self) -> ScientificReadinessLevel:
        return ScientificReadinessLevel.SRL_3
        
    @property
    def contract(self) -> ScientificContract:
        return ScientificContract(
            purpose="Time-frequency representation using Continuous Wavelet Transform",
            mathematical_assumptions=[
                "Finite energy signal", 
                "Admissibility condition of wavelet"
            ],
            numerical_assumptions=[
                "Complex Morlet wavelet",
                "Linear frequency spacing"
            ],
            computational_assumptions=[
                "FFT convolution is used for efficiency"
            ],
            supported_modalities=[SignalType.EEG, SignalType.ECOG, SignalType.SEEG, SignalType.LFP],
            unsupported_modalities=[],
            failure_conditions=["Edge artifacts (cone of influence)"],
            known_artifacts=["Time-frequency resolution tradeoff (Heisenberg-Gabor)"],
            expected_uncertainty=["Edge effects at start/end of signal"],
            validation_papers=["10.1109/78.84777"],
            reference_implementations=["scipy.signal.cwt", "scipy.signal.morlet2"],
            reference_software=["SciPy"],
            expected_numerical_tolerances={"cwt_error": 1e-5},
            calibration_provenance="Analytical function"
        )
        
    @property
    def capabilities(self) -> List[PluginCapability]:
        return [PluginCapability(
            id="time_frequency_analysis",
            version="0.1.0",
            consumes=["ISignal"],
            produces=["ISignal"],
            assumptions=["Signal contains non-stationary oscillations"],
            uncertainty_model=["Resolution bounding box"]
        )]
        
    @property
    def inputs(self) -> List[Type[IScientificObject]]:
        return [ISignal]
        
    @property
    def outputs(self) -> List[Type[IScientificObject]]:
        return [ISignal]
        
    def execute(self, inputs: Dict[str, IScientificObject]) -> Dict[str, IScientificObject]:
        signal = inputs.get("signal")
        if not isinstance(signal, ISignal):
            raise ValueError("Expected ISignal as 'signal' input")
            
        data = signal.data
        fs = signal.sampling_rate
        
        import scipy.signal
        n_channels = data.shape[1]
        
        # Calculate scales for Morlet wavelet
        w = 6.0
        scales = w * fs / (2 * np.pi * self.freqs)
        
        cwt_data = []
        for ch in range(n_channels):
            # scipy.signal.cwt output shape: (len(scales), len(data))
            cwt_mat = scipy.signal.cwt(data[:, ch], scipy.signal.morlet2, scales, w=w)
            cwt_data.append(np.abs(cwt_mat))
            
        # Shape: (time, freqs, channels)
        cwt_data = np.stack(cwt_data, axis=-1)
        cwt_data = np.transpose(cwt_data, (1, 0, 2))
        
        return {"cwt": ISignal(sampling_rate=fs, data=cwt_data)}
