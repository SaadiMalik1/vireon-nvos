import numpy as np
from typing import Dict, List, Type
from vireon_core.contracts.plugin import (
    IPlugin, ScientificContract, ScientificReadinessLevel, PluginCapability
)
from vireon_core.contracts.base import IScientificObject, ISignal, SignalType
from vireon_core.runtime.rng import DeterministicRNG

class ADCQuantizationModel(IPlugin):
    """Simulates ADC bit-depth quantization and LSB resolution."""
    def __init__(self, bit_depth: int = 16, vref_uv: float = 4500000.0, gain: float = 24.0):
        self.bit_depth = bit_depth
        self.vref_uv = vref_uv
        self.gain = gain
        self.lsb_uv = (self.vref_uv / self.gain) / (2**self.bit_depth - 1)

    @property
    def plugin_id(self) -> str:
        return "vk:Hardware:ADCQuantization"

    @property
    def version(self) -> str:
        return "0.1.0"

    @property
    def srl(self) -> ScientificReadinessLevel:
        return ScientificReadinessLevel.SRL_2

    @property
    def contract(self) -> ScientificContract:
        return ScientificContract(
            purpose="Simulate ADC bit-depth limitations and LSB quantization noise",
            mathematical_assumptions=["Linear quantization mapping"],
            hardware_assumptions=[f"{self.bit_depth}-bit ADC", f"Gain: {self.gain}x"],
            supported_modalities=[SignalType.EEG, SignalType.ECOG, SignalType.SEEG, SignalType.LFP, SignalType.EMG, SignalType.EOG],
            unsupported_modalities=[],
            numerical_assumptions=["Rounding to nearest LSB"],
            known_artifacts=["Quantization noise"],
            expected_uncertainty=["LSB^2 / 12 variance"],
            reference_implementations=["Standard DSP quantization formulas"],
            reference_software=["None"],
            expected_numerical_tolerances={"quantization_error": self.lsb_uv},
            calibration_provenance="Hardware specification sheet"
        )

    @property
    def capabilities(self) -> List[PluginCapability]:
        return [PluginCapability(
            id="hardware_simulation",
            version="0.1.0",
            consumes=["ISignal"],
            produces=["ISignal"],
            assumptions=["Ideal uniform quantizer"],
            uncertainty_model=["Quantization noise variance (LSB^2 / 12)"]
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
        
        quantized = np.round(signal.data / self.lsb_uv) * self.lsb_uv
        return {"signal": ISignal(sampling_rate=signal.sampling_rate, data=quantized)}

class AmplifierSaturationModel(IPlugin):
    """Simulates amplifier hard and soft clipping."""
    def __init__(self, max_uv: float = 187500.0, soft_clip_knee: float = 0.9):
        self.max_uv = max_uv
        self.soft_clip_knee = soft_clip_knee

    @property
    def plugin_id(self) -> str:
        return "vk:Hardware:AmplifierSaturation"

    @property
    def version(self) -> str:
        return "0.1.0"

    @property
    def srl(self) -> ScientificReadinessLevel:
        return ScientificReadinessLevel.SRL_2

    @property
    def contract(self) -> ScientificContract:
        return ScientificContract(
            purpose="Simulate analog amplifier voltage saturation",
            mathematical_assumptions=["Symmetric clipping", "Tanh soft-clipping function"],
            hardware_assumptions=[f"Max input range: +/-{self.max_uv}uV"],
            supported_modalities=[SignalType.EEG, SignalType.ECOG, SignalType.SEEG, SignalType.LFP],
            unsupported_modalities=[],
            numerical_assumptions=["Float64 precision for tanh compression"],
            known_artifacts=["Harmonic distortion from clipping"],
            expected_uncertainty=["Signal truncation"],
            reference_implementations=["Standard tanh compression"],
            reference_software=["None"],
            expected_numerical_tolerances={"clipping_bound": 1e-10},
            calibration_provenance="Hardware specification sheet"
        )

    @property
    def capabilities(self) -> List[PluginCapability]:
        return [PluginCapability(
            id="hardware_simulation",
            version="0.1.0",
            consumes=["ISignal"],
            produces=["ISignal"],
            assumptions=["Static nonlinearity without hysteresis"],
            uncertainty_model=["Deterministic clipping"]
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
        
        data = np.copy(signal.data)
        data = np.clip(data, -self.max_uv, self.max_uv)
        
        if self.soft_clip_knee < 1.0:
            knee_thresh = self.max_uv * self.soft_clip_knee
            mask = np.abs(data) > knee_thresh
            over = np.abs(data[mask]) - knee_thresh
            denominator = self.max_uv - knee_thresh
            if denominator > 0:
                compressed = knee_thresh + denominator * np.tanh(over / denominator)
                data[mask] = np.sign(data[mask]) * compressed
            
        return {"signal": ISignal(sampling_rate=signal.sampling_rate, data=data)}

class SamplingJitterModel(IPlugin):
    """Simulates stochastic sampling time jitter."""
    def __init__(self, jitter_std_s: float = 0.001, seed: int = 42):
        self.jitter_std_s = jitter_std_s
        self.rng = DeterministicRNG(seed)

    @property
    def plugin_id(self) -> str:
        return "vk:Hardware:SamplingJitter"

    @property
    def version(self) -> str:
        return "0.1.0"

    @property
    def srl(self) -> ScientificReadinessLevel:
        return ScientificReadinessLevel.SRL_2

    @property
    def contract(self) -> ScientificContract:
        return ScientificContract(
            purpose="Simulate stochastic clock jitter in ADC sampling",
            mathematical_assumptions=["Gaussian jitter distribution", "Linear interpolation for resampling"],
            numerical_assumptions=["Monotonically increasing time vector"],
            supported_modalities=[SignalType.EEG, SignalType.ECOG, SignalType.SEEG],
            unsupported_modalities=[],
            known_artifacts=["Phase noise", "High frequency attenuation"],
            expected_uncertainty=["Gaussian variance on timestamp"],
            reference_implementations=["np.interp"],
            reference_software=["NumPy"],
            expected_numerical_tolerances={"interpolation_error": 1e-6},
            calibration_provenance="Hardware clock drift specifications"
        )

    @property
    def capabilities(self) -> List[PluginCapability]:
        return [PluginCapability(
            id="hardware_simulation",
            version="0.1.0",
            consumes=["ISignal"],
            produces=["ISignal"],
            assumptions=["Uncorrelated jitter across samples", "Linear signal behavior between samples"],
            uncertainty_model=["Gaussian phase noise"]
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
        
        if self.jitter_std_s <= 0:
            return {"signal": ISignal(sampling_rate=fs, data=data)}
            
        n_samples, n_channels = data.shape
        t = np.arange(n_samples) / fs
        
        t_jittered = t + self.rng.normal(size=n_samples) * self.jitter_std_s
        
        jittered_data = np.zeros_like(data)
        for ch in range(n_channels):
            jittered_data[:, ch] = np.interp(t_jittered, t, data[:, ch])
            
        return {"signal": ISignal(sampling_rate=fs, data=jittered_data)}

class PacketLossModel(IPlugin):
    """Simulates wireless transmission packet loss or buffer overflows."""
    def __init__(self, drop_prob: float = 0.01, burst_length: int = 5, fill_value: float = np.nan, seed: int = 42):
        self.drop_prob = drop_prob
        self.burst_length = burst_length
        self.fill_value = fill_value
        self.rng = DeterministicRNG(seed)

    @property
    def plugin_id(self) -> str:
        return "vk:Hardware:PacketLoss"

    @property
    def version(self) -> str:
        return "0.1.0"

    @property
    def srl(self) -> ScientificReadinessLevel:
        return ScientificReadinessLevel.SRL_2

    @property
    def contract(self) -> ScientificContract:
        return ScientificContract(
            purpose="Simulate wireless data transmission packet loss",
            mathematical_assumptions=["Bernoulli trial for packet drop", "Fixed burst length drop"],
            supported_modalities=[SignalType.EEG, SignalType.ECOG],
            unsupported_modalities=[],
            numerical_assumptions=["NaN substitution for missing data"],
            known_artifacts=["Discontinuities", "Missing data segments"],
            expected_uncertainty=["Missing completely at random (MCAR)"],
            reference_implementations=["Synthetic drop injection"],
            reference_software=["None"],
            expected_numerical_tolerances={"drop_rate": 1e-2},
            calibration_provenance="Telemetry protocol analysis"
        )

    @property
    def capabilities(self) -> List[PluginCapability]:
        return [PluginCapability(
            id="hardware_simulation",
            version="0.1.0",
            consumes=["ISignal"],
            produces=["ISignal"],
            assumptions=["Drops occur independently across time chunks"],
            uncertainty_model=["Missing completely at random (MCAR) approximation"]
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
        n_samples = data.shape[0]
        
        drops = self.rng.uniform(size=n_samples) < self.drop_prob
        data_dropped = data.copy()
        drop_indices = np.where(drops)[0]
        
        for idx in drop_indices:
            end_idx = min(n_samples, idx + self.burst_length)
            data_dropped[idx:end_idx, :] = self.fill_value
            
        return {"signal": ISignal(sampling_rate=fs, data=data_dropped)}

class ADS1299:
    """TI ADS1299 EEG analog front-end model.

    Datasheet: SBAS499C (revision C, 2018).
    Key specs:
    - Input-referred noise: 1.0 µVpp (250 SPS, gain=24)
    - Input impedance: 1 GΩ
    - CMRR: -110 dB
    - ADC resolution: 24 bit
    - Programmable gain: 1, 2, 4, 6, 8, 12, 24
    - Sample rates: 250, 500, 1000, 2000, 4000, 8000, 16000 SPS
    """
    def __init__(self, gain: int = 24, sample_rate: int = 250,
                 rng: DeterministicRNG = None):
        self.gain = gain
        self.sample_rate = sample_rate
        self.rng = rng or DeterministicRNG(42)
        # Input-referred noise from datasheet Table 1
        self.input_noise_vpp = {250: 1.0, 500: 1.5, 1000: 2.0, 2000: 2.5}.get(sample_rate, 2.0)
        self.lsb_uv = (4.5 / (gain * 2**23)) * 1e6  # V to µV, 24-bit ADC

    def process(self, signal_uv: np.ndarray) -> np.ndarray:
        """Apply ADS1299 acquisition model to signal (in µV)."""
        # 1. Add input-referred noise (Gaussian approximation of datasheet noise)
        noise_rms = self.input_noise_vpp / 6.6  # Vpp to RMS (6.6 sigma for 99.9%)
        noise = self.rng.normal(0, noise_rms, size=signal_uv.shape)
        # 2. Apply gain
        amplified = (signal_uv + noise) * self.gain
        # 3. Quantize (24-bit ADC)
        quantized = np.round(amplified / self.lsb_uv) * self.lsb_uv
        # 4. Convert back to input-referred µV
        return quantized / self.gain


import numpy as np

