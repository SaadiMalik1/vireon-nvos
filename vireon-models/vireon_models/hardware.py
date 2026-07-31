import numpy as np

class HardwareDigitalTwin:
    """
    Base class for physical acquisition hardware simulations (Phase E).
    """
    def simulate(self, signal: np.ndarray) -> np.ndarray:
        raise NotImplementedError

class AmplifierTwin(HardwareDigitalTwin):
    def __init__(self, saturation_uv: float, impedance_kohm: float, input_noise_uv: float):
        self.saturation_uv = saturation_uv
        self.impedance = impedance_kohm
        self.input_noise = input_noise_uv
        
    def simulate(self, signal: np.ndarray) -> np.ndarray:
        # 1. Add thermal noise scaled by impedance
        noise = np.random.normal(0, self.input_noise * (1 + 0.1 * self.impedance), signal.shape)
        noisy_signal = signal + noise
        
        # 2. Apply saturation clipping
        clipped_signal = np.clip(noisy_signal, -self.saturation_uv, self.saturation_uv)
        
        return clipped_signal

class TelemetryTwin(HardwareDigitalTwin):
    def __init__(self, packet_loss_rate: float, jitter_ms: float):
        self.packet_loss_rate = packet_loss_rate
        self.jitter_ms = jitter_ms
        
    def simulate(self, signal: np.ndarray) -> np.ndarray:
        n_samples = signal.shape[-1]
        
        # Simulate packet loss (dropout blocks of 8 samples)
        packet_size = 8
        n_packets = n_samples // packet_size
        
        loss_mask = np.random.rand(n_packets) < self.packet_loss_rate
        
        out_signal = signal.copy()
        for i, lost in enumerate(loss_mask):
            if lost:
                start = i * packet_size
                end = start + packet_size
                out_signal[..., start:end] = 0 # Drop packet
                
        return out_signal

class BatteryDegradationTwin(HardwareDigitalTwin):
    def __init__(self, charge_percent: float):
        self.charge = charge_percent
        
    def simulate(self, signal: np.ndarray) -> np.ndarray:
        # If battery is low, increase baseline drift and noise
        if self.charge < 15.0:
            drift = np.linspace(0, 50, signal.shape[-1])
            noise = np.random.normal(0, 5.0, signal.shape)
            return signal + drift + noise
        return signal
