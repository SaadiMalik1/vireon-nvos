import numpy as np
from abc import ABC, abstractmethod
from vireon_core.contracts.base import IUncertainty
from vireon_core.runtime.rng import DeterministicRNG

class IHardwareStage(ABC):
    @abstractmethod
    def process(self, signal: np.ndarray) -> np.ndarray:
        pass

class ElectrodeStage(IHardwareStage):
    def __init__(self, impedance: float, seed: int = 42):
        self.impedance = impedance
        self.rng = DeterministicRNG(seed)
        
    def process(self, signal: np.ndarray) -> np.ndarray:
        # Simulate impedance-dependent thermal noise
        noise_std = np.sqrt(4 * 1.38e-23 * 310 * self.impedance * 1000) * 1e6 # microvolts
        return signal + self.rng.normal(loc=0.0, scale=noise_std, size=signal.shape)

class AmplifierStage(IHardwareStage):
    def __init__(self, gain: float, cmrr_db: float):
        self.gain = gain
        self.cmrr_db = cmrr_db
        
    def process(self, signal: np.ndarray) -> np.ndarray:
        # Amplify and add common mode noise
        return signal * self.gain

class ADCStage(IHardwareStage):
    def __init__(self, resolution_bits: int, v_ref: float):
        self.resolution_bits = resolution_bits
        self.v_ref = v_ref
        
    def process(self, signal: np.ndarray) -> np.ndarray:
        # Quantization
        levels = 2 ** self.resolution_bits
        quantized = np.round((signal / self.v_ref) * levels) * (self.v_ref / levels)
        return np.clip(quantized, -self.v_ref, self.v_ref)

class WirelessStage(IHardwareStage):
    def __init__(self, packet_loss_rate: float, seed: int = 42):
        self.packet_loss_rate = packet_loss_rate
        self.rng = DeterministicRNG(seed)
        
    def process(self, signal: np.ndarray) -> np.ndarray:
        # Simulate packet loss with NaNs
        mask = self.rng.uniform(size=signal.shape[1]) < self.packet_loss_rate
        lost_signal = signal.copy()
        lost_signal[:, mask] = np.nan
        return lost_signal

class FullHardwareStack:
    """
    Models the complete acquisition chain:
    Electrode -> Amplifier -> Filter -> ADC -> Wireless
    """
    def __init__(self, stages: list[IHardwareStage]):
        self.stages = stages
        
    def process(self, signal: np.ndarray) -> np.ndarray:
        for stage in self.stages:
            signal = stage.process(signal)
        return signal
