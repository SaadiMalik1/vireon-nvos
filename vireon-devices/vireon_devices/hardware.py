import numpy as np
from typing import Dict, Any
from vireon_core.contracts.device import ReferenceDevice

class ADCModel:
    """
    Simulates Analog-to-Digital Converter hardware constraints (Quantization & Saturation).
    """
    def __init__(self, bit_depth: int = 24, v_ref_uv: float = 4500000.0, gain: float = 24.0):
        self.bit_depth = bit_depth
        self.v_ref_uv = v_ref_uv
        self.gain = gain
        
        # Total number of discrete steps
        self.levels = 2 ** self.bit_depth
        
        # Max input range (symmetric around 0)
        self.v_max = (self.v_ref_uv / self.gain) / 2.0
        self.v_min = -self.v_max
        
        # LSB (Least Significant Bit) resolution in microvolts
        self.lsb = (self.v_max - self.v_min) / (self.levels - 1)

    def process(self, signal: np.ndarray) -> np.ndarray:
        # Clip to dynamic range
        clipped = np.clip(signal, self.v_min, self.v_max)
        
        # Quantize
        quantized_steps = np.round((clipped - self.v_min) / self.lsb)
        
        # Reconstruct voltage
        return (quantized_steps * self.lsb) + self.v_min

class AmplifierModel:
    """
    Simulates the Analog Front-End (Thermal Noise, Powerline Hum).
    """
    def __init__(self, noise_rms_uv: float = 1.0, powerline_freq: float = 50.0, powerline_amp_uv: float = 5.0, seed: int = 42):
        self.noise_rms_uv = noise_rms_uv
        self.powerline_freq = powerline_freq
        self.powerline_amp_uv = powerline_amp_uv
        self.rng = np.random.default_rng(seed)

    def process(self, signal: np.ndarray, sample_rate: float) -> np.ndarray:
        num_samples = signal.shape[0]
        num_channels = signal.shape[1]
        t = np.linspace(0, num_samples / sample_rate, num_samples, endpoint=False)
        
        # Thermal white noise
        noise = self.rng.normal(0, self.noise_rms_uv, signal.shape).astype(np.float32)
        
        # Powerline interference
        hum = np.sin(2 * np.pi * self.powerline_freq * t) * self.powerline_amp_uv
        hum_2d = np.tile(hum[:, np.newaxis], (1, num_channels))
        
        return signal + noise + hum_2d

class ADS1299(ReferenceDevice):
    """
    Concrete model of the Texas Instruments ADS1299 (used in OpenBCI).
    """
    def __init__(self):
        super().__init__(name="ADS1299", specs={
            "bit_depth": 24,
            "v_ref_uv": 4500000.0,
            "gain": 24.0,
            "input_noise_rms_uv": 1.0,
        })
        self.adc = ADCModel(bit_depth=24, v_ref_uv=4500000.0, gain=24.0)
        self.amp = AmplifierModel(noise_rms_uv=1.0)
        
    def process(self, signal: np.ndarray, sample_rate: float) -> np.ndarray:
        amplified = self.amp.process(signal, sample_rate)
        quantized = self.adc.process(amplified)
        return quantized
