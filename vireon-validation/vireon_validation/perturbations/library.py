import numpy as np
from vireon_core.runtime.rng import DeterministicRNG

class PerturbationModel:
    def __init__(self, name: str, severity: float, seed: int = 42):
        self.name = name
        self.severity = severity
        self.seed = seed
        self.rng = DeterministicRNG(seed)
        
    def apply(self, data: np.ndarray) -> np.ndarray:
        raise NotImplementedError

    def __call__(self, data: np.ndarray) -> np.ndarray:
        return self.apply(data)

class WhiteNoisePerturbation(PerturbationModel):
    def __init__(self, name: str = "WhiteNoise", severity: float = 0.5, seed: int = 42):
        super().__init__(name=name, severity=severity, seed=seed)

    def apply(self, data: np.ndarray) -> np.ndarray:
        # severity implies noise standard deviation
        noise = self.rng.normal(0, self.severity, size=data.shape)
        return data + noise

class ChannelDropoutPerturbation(PerturbationModel):
    def __init__(self, name: str = "ChannelDropout", severity: float = 0.2, seed: int = 42):
        super().__init__(name=name, severity=severity, seed=seed)

    def apply(self, data: np.ndarray) -> np.ndarray:
        # severity implies percentage of channels dropped
        n_channels = data.shape[-2]
        n_drop = max(1, int(n_channels * self.severity))
        # Deterministic choice of unique channels
        keys = self.rng.uniform(0.0, 1.0, size=n_channels)
        drop_indices = np.argsort(keys)[:n_drop]
        perturbed_data = data.copy()
        perturbed_data[..., drop_indices, :] = 0
        return perturbed_data

class LineNoisePerturbation(PerturbationModel):
    def __init__(self, severity: float, freq: float = 50.0, fs: float = 256.0, name: str = "LineNoise", seed: int = 42):
        super().__init__(name=name, severity=severity, seed=seed)
        self.freq = freq
        self.fs = fs
        
    def apply(self, data: np.ndarray) -> np.ndarray:
        # severity implies amplitude of the line noise
        n_times = data.shape[-1]
        t = np.arange(n_times) / self.fs
        noise = self.severity * np.sin(2 * np.pi * self.freq * t)
        return data + noise

class QuantizationPerturbation(PerturbationModel):
    def __init__(self, severity: float, name: str = "Quantization", seed: int = 42):
        super().__init__(name=name, severity=severity, seed=seed)

    def apply(self, data: np.ndarray) -> np.ndarray:
        # severity implies number of bits (e.g. 8 bit)
        if self.severity <= 0: return data
        bits = int(self.severity)
        scale = 2 ** bits
        return np.round(data * scale) / scale
