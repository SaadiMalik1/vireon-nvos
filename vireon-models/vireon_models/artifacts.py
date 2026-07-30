import numpy as np
from typing import Dict, List, Type
from vireon_core.contracts.plugin import (
    IPlugin, ScientificContract, ScientificReadinessLevel, PluginCapability
)
from vireon_core.contracts.base import IScientificObject, ISignal, SignalType

class OcularArtifactGenerator(IPlugin):
    """Injects simulated EOG blink artifacts into EEG data."""
    def __init__(self, blink_rate_hz: float = 0.3, amplitude_uv: float = 100.0, channel_weights: list = None):
        self.blink_rate_hz = blink_rate_hz
        self.amplitude_uv = amplitude_uv
        self.channel_weights = channel_weights # Frontal channels should have higher weights

    @property
    def plugin_id(self) -> str:
        return "vk:Artifact:OcularBlink"

    @property
    def version(self) -> str:
        return "0.1.0"

    @property
    def srl(self) -> ScientificReadinessLevel:
        return ScientificReadinessLevel.SRL_1

    @property
    def contract(self) -> ScientificContract:
        return ScientificContract(
            purpose="Simulate realistic physiological EOG blinks for artifact rejection benchmarking",
            mathematical_assumptions=["Poisson process for blink timing", "Fixed blink morphology (bell-curve)"],
            supported_modalities=[SignalType.EEG],
            unsupported_modalities=[SignalType.SEEG, SignalType.ECOG, SignalType.LFP],
            failure_conditions=["Sampling rate < 10Hz"],
            known_artifacts=["OcularBlink"],
            expected_uncertainty=["Fixed amplitude uncertainty"],
            reference_implementations=["MNE-Python blink templates"],
            reference_software=["MNE"],
            expected_numerical_tolerances={"amplitude": 1e-6},
            calibration_provenance="Synthetic"
        )

    @property
    def capabilities(self) -> List[PluginCapability]:
        return [PluginCapability(
            id="artifact_injection",
            version="0.1.0",
            consumes=["ISignal"],
            produces=["ISignal"],
            assumptions=["Additive noise model"],
            uncertainty_model=["Fixed amplitude scalar"]
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
        
        n_samples, n_channels = data.shape
        weights = self.channel_weights if self.channel_weights else [1.0] * n_channels
        
        blink_prob = self.blink_rate_hz / fs
        blinks = np.random.rand(n_samples) < blink_prob
        
        blink_len = int(0.4 * fs)
        if blink_len > 0:
            t = np.linspace(0, np.pi, blink_len)
            template = np.sin(t) ** 2  # simple bell-like shape
            
            artifact = np.zeros_like(data)
            blink_indices = np.where(blinks)[0]
            
            for idx in blink_indices:
                if idx + blink_len < n_samples:
                    for ch in range(n_channels):
                        artifact[idx:idx+blink_len, ch] += template * self.amplitude_uv * weights[ch]
                        
            new_data = data + artifact
        else:
            new_data = data
            
        return {"signal": ISignal(sampling_rate=fs, data=new_data)}

class EMGArtifactGenerator(IPlugin):
    """Injects high-frequency muscle noise."""
    def __init__(self, active_prob: float = 0.1, max_amplitude_uv: float = 50.0):
        self.active_prob = active_prob
        self.max_amplitude_uv = max_amplitude_uv

    @property
    def plugin_id(self) -> str:
        return "vk:Artifact:EMGNoise"

    @property
    def version(self) -> str:
        return "0.1.0"

    @property
    def srl(self) -> ScientificReadinessLevel:
        return ScientificReadinessLevel.SRL_1

    @property
    def contract(self) -> ScientificContract:
        return ScientificContract(
            purpose="Simulate high-frequency muscle artifacts for spatial filter benchmarking",
            mathematical_assumptions=["Random walk envelope", "White noise bursts"],
            supported_modalities=[SignalType.EEG, SignalType.ECOG, SignalType.SEEG],
            unsupported_modalities=[SignalType.LFP],
            failure_conditions=["Sampling rate < 200Hz"],
            known_artifacts=["EMGNoise"],
            expected_uncertainty=["Gaussian amplitude distribution"],
            reference_implementations=["Synthetic generative models"],
            reference_software=["None"],
            expected_numerical_tolerances={"mean_zero": 1e-3},
            calibration_provenance="Synthetic"
        )

    @property
    def capabilities(self) -> List[PluginCapability]:
        return [PluginCapability(
            id="artifact_injection",
            version="0.1.0",
            consumes=["ISignal"],
            produces=["ISignal"],
            assumptions=["Additive noise model"],
            uncertainty_model=["Gaussian"]
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
        n_samples, n_channels = data.shape
        
        tension = np.convolve(np.random.randn(n_samples), np.ones(int(max(1, fs)))/fs, mode='same')
        tension = np.clip(tension * 10, 0, 1) # threshold for active bursts
        
        noise = np.random.randn(n_samples, n_channels) * self.max_amplitude_uv
        artifact = noise * tension[:, np.newaxis]
        
        return {"signal": ISignal(sampling_rate=fs, data=data + artifact)}

class ElectrodePopGenerator(IPlugin):
    """Injects sudden transient step functions simulating loose electrodes."""
    def __init__(self, pop_rate_hz: float = 0.05, amplitude_uv: float = 500.0, decay_time_s: float = 1.0):
        self.pop_rate_hz = pop_rate_hz
        self.amplitude_uv = amplitude_uv
        self.decay_time_s = decay_time_s

    @property
    def plugin_id(self) -> str:
        return "vk:Artifact:ElectrodePop"

    @property
    def version(self) -> str:
        return "0.1.0"

    @property
    def srl(self) -> ScientificReadinessLevel:
        return ScientificReadinessLevel.SRL_1

    @property
    def contract(self) -> ScientificContract:
        return ScientificContract(
            purpose="Simulate transient electrode popping artifacts",
            mathematical_assumptions=["Exponential decay", "Step-function transient"],
            supported_modalities=[SignalType.EEG, SignalType.ECOG],
            unsupported_modalities=[SignalType.SEEG, SignalType.LFP],
            known_artifacts=["ElectrodePop"],
            expected_uncertainty=["Uniform step amplitude"],
            reference_implementations=["Synthetic transient models"],
            reference_software=["None"],
            expected_numerical_tolerances={"amplitude": 1e-6},
            calibration_provenance="Synthetic"
        )

    @property
    def capabilities(self) -> List[PluginCapability]:
        return [PluginCapability(
            id="artifact_injection",
            version="0.1.0",
            consumes=["ISignal"],
            produces=["ISignal"],
            assumptions=["Additive step transient"],
            uncertainty_model=["Uniform step amplitude"]
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
        n_samples, n_channels = data.shape
        pop_prob = self.pop_rate_hz / fs
        
        artifact = np.zeros_like(data)
        
        for ch in range(n_channels):
            pops = np.random.rand(n_samples) < pop_prob
            pop_indices = np.where(pops)[0]
            
            decay = np.exp(-np.arange(n_samples) / (self.decay_time_s * fs))
            
            for idx in pop_indices:
                length = n_samples - idx
                artifact[idx:, ch] += decay[:length] * self.amplitude_uv * (np.random.rand() > 0.5 and 1 or -1)
                
        return {"signal": ISignal(sampling_rate=fs, data=data + artifact)}

class ImpedanceDriftGenerator(IPlugin):
    """Injects low-frequency stochastic baseline wandering."""
    def __init__(self, drift_strength: float = 20.0, cutoff_hz: float = 0.1):
        self.drift_strength = drift_strength
        self.cutoff_hz = cutoff_hz

    @property
    def plugin_id(self) -> str:
        return "vk:Artifact:ImpedanceDrift"

    @property
    def version(self) -> str:
        return "0.1.0"

    @property
    def srl(self) -> ScientificReadinessLevel:
        return ScientificReadinessLevel.SRL_1

    @property
    def contract(self) -> ScientificContract:
        return ScientificContract(
            purpose="Simulate slow baseline wandering due to skin-electrode impedance changes",
            mathematical_assumptions=["Low-pass filtered white noise", "2nd order Butterworth filter"],
            supported_modalities=[SignalType.EEG, SignalType.ECOG],
            unsupported_modalities=[SignalType.SEEG, SignalType.LFP],
            numerical_assumptions=["Filter stability dependent on fs vs cutoff_hz"],
            known_artifacts=["ImpedanceDrift"],
            expected_uncertainty=["Filtered Gaussian process variance"],
            reference_implementations=["scipy.signal.butter"],
            reference_software=["SciPy"],
            expected_numerical_tolerances={"filter_stability": 1e-10},
            calibration_provenance="Synthetic"
        )

    @property
    def capabilities(self) -> List[PluginCapability]:
        return [PluginCapability(
            id="artifact_injection",
            version="0.1.0",
            consumes=["ISignal"],
            produces=["ISignal"],
            assumptions=["Additive low-frequency drift"],
            uncertainty_model=["Gaussian filtered process"]
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
        n_samples, n_channels = data.shape
        
        noise = np.random.randn(n_samples, n_channels)
        
        import scipy.signal
        nyq = 0.5 * fs
        if self.cutoff_hz >= nyq:
            raise ValueError(f"Cutoff frequency {self.cutoff_hz} must be strictly less than Nyquist {nyq}")
            
        b, a = scipy.signal.butter(2, self.cutoff_hz / nyq, btype='low')
        
        drift = scipy.signal.filtfilt(b, a, noise, axis=0)
        # Handle zero std case to prevent NaNs (numerical robustness)
        std_drift = np.std(drift, axis=0)
        std_drift[std_drift == 0] = 1e-12 
        drift = (drift / std_drift) * self.drift_strength
        
        return {"signal": ISignal(sampling_rate=fs, data=data + drift)}
