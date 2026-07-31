import numpy as np
from typing import Optional
from vireon_core.contracts.base import ISignal
from vireon_core.runtime.rng import DeterministicRNG

class PhysiologicalPerturbations:
    @staticmethod
    def add_eye_blink(signal: ISignal, latency: float, amplitude: float = 50.0) -> ISignal:
        """
        Adds a simulated EOG eye blink artifact.
        """
        sfreq = signal.sampling_rate
        t = np.arange(signal.data.shape[0]) / sfreq
        blink = amplitude * np.exp(-((t - latency) ** 2) / (2 * (0.02 ** 2)))
        new_data = signal.data + np.tile(blink, (signal.data.shape[1], 1)).T
        return ISignal(sampling_rate=sfreq, data=new_data)

class HardwarePerturbations:
    @staticmethod
    def add_quantization_noise(signal: ISignal, bit_depth: int = 16, v_range: float = 200.0) -> ISignal:
        """
        Simulates ADC quantization.
        """
        levels = 2 ** bit_depth
        step = (2 * v_range) / levels
        quantized_data = np.round(signal.data / step) * step
        return ISignal(sampling_rate=signal.sampling_rate, data=quantized_data)

    @staticmethod
    def simulate_packet_loss(signal: ISignal, loss_probability: float = 0.05, seed: int = 42) -> ISignal:
        """
        Simulates dropped Bluetooth/Wifi packets by zeroing out random samples.
        """
        rng = DeterministicRNG(seed=seed)
        mask = rng.uniform(0, 1, signal.data.shape) > loss_probability
        new_data = signal.data * mask
        return ISignal(sampling_rate=signal.sampling_rate, data=new_data)

class MathematicalPerturbations:
    @staticmethod
    def add_baseline_drift(signal: ISignal, slope: float = 0.5) -> ISignal:
        """
        Adds a linear drift to the signal.
        """
        t = np.arange(signal.data.shape[0]) / signal.sampling_rate
        drift = slope * t
        new_data = signal.data + np.tile(drift, (signal.data.shape[1], 1)).T
        return ISignal(sampling_rate=signal.sampling_rate, data=new_data)
