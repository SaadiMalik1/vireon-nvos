import numpy as np

class PerturbationModel:
    def __init__(self, name: str, severity: float):
        self.name = name
        self.severity = severity
        
    def apply(self, data: np.ndarray) -> np.ndarray:
        raise NotImplementedError

class WhiteNoisePerturbation(PerturbationModel):
    def apply(self, data: np.ndarray) -> np.ndarray:
        # severity implies noise standard deviation
        noise = np.random.normal(0, self.severity, size=data.shape)
        return data + noise

class ChannelDropoutPerturbation(PerturbationModel):
    def apply(self, data: np.ndarray) -> np.ndarray:
        # severity implies percentage of channels dropped
        n_channels = data.shape[-2]
        n_drop = int(n_channels * self.severity)
        drop_indices = np.random.choice(n_channels, n_drop, replace=False)
        perturbed_data = data.copy()
        perturbed_data[..., drop_indices, :] = 0
        return perturbed_data

class LineNoisePerturbation(PerturbationModel):
    def __init__(self, severity: float, freq: float = 50.0, fs: float = 256.0):
        super().__init__("LineNoise", severity)
        self.freq = freq
        self.fs = fs
        
    def apply(self, data: np.ndarray) -> np.ndarray:
        # severity implies amplitude of the line noise
        n_times = data.shape[-1]
        t = np.arange(n_times) / self.fs
        noise = self.severity * np.sin(2 * np.pi * self.freq * t)
        return data + noise

class QuantizationPerturbation(PerturbationModel):
    def apply(self, data: np.ndarray) -> np.ndarray:
        # severity implies number of bits (e.g. 8 bit)
        if self.severity <= 0: return data
        bits = int(self.severity)
        scale = 2 ** bits
        return np.round(data * scale) / scale
