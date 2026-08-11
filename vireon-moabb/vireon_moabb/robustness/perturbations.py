import numpy as np
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class PerturbationResult:
    """Result of a single perturbation."""
    name: str
    severity: float
    perturbed_data: np.ndarray
    baseline_data: np.ndarray
    metadata: dict


class Perturbation(ABC):
    """Base class for data perturbations."""

    def __init__(self, severity: float, seed: int = 42):
        assert 0.0 <= severity <= 1.0, "Severity must be in [0, 1]"
        self.severity = severity
        self.seed = seed

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def apply(self, data: np.ndarray) -> np.ndarray:
        pass


class ChannelDropout(Perturbation):
    """Randomly zero out channels."""

    @property
    def name(self) -> str:
        return "channel_dropout"

    def apply(self, data: np.ndarray) -> np.ndarray:
        rng = np.random.default_rng(self.seed)
        n_channels = data.shape[-2]
        n_drop = max(1, int(self.severity * n_channels))
        drop_idx = rng.choice(n_channels, size=n_drop, replace=False)

        perturbed = data.copy()
        perturbed[..., drop_idx, :] = 0
        return perturbed


class WhiteNoise(Perturbation):
    """Add Gaussian white noise."""

    @property
    def name(self) -> str:
        return "white_noise"

    def apply(self, data: np.ndarray) -> np.ndarray:
        rng = np.random.default_rng(self.seed)
        signal_std = np.std(data)
        noise_std = self.severity * signal_std
        noise = rng.normal(0, noise_std, data.shape)
        return data + noise


class LineNoise(Perturbation):
    """Add 50/60 Hz line noise."""

    @property
    def name(self) -> str:
        return "line_noise"

    def apply(self, data: np.ndarray) -> np.ndarray:
        fs = 250
        t = np.arange(data.shape[-1]) / fs
        line_freq = 50
        amplitude = self.severity * np.std(data) * 0.5
        noise = amplitude * np.sin(2 * np.pi * line_freq * t)
        return data + noise[None, None, :] if data.ndim == 3 else data + noise[None, :]


class TimeShift(Perturbation):
    """Shift data in time."""

    @property
    def name(self) -> str:
        return "time_shift"

    def apply(self, data: np.ndarray) -> np.ndarray:
        n_samples = data.shape[-1]
        shift = int(self.severity * n_samples * 0.1)
        return np.roll(data, shift, axis=-1)


class AmplitudeScaling(Perturbation):
    """Scale amplitude of channels."""

    @property
    def name(self) -> str:
        return "amplitude_scaling"

    def apply(self, data: np.ndarray) -> np.ndarray:
        rng = np.random.default_rng(self.seed)
        n_channels = data.shape[-2]
        scales = 1 + rng.uniform(-self.severity, self.severity, n_channels)
        return data * scales[None, :, None] if data.ndim == 3 else data * scales[:, None]
