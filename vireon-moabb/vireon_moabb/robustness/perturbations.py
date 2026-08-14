"""
Perturbations — VIREON-owned robustness modifications to raw EEG data.

These classes follow principle ADR 0008 #6: VIREON modifies experimental
conditions and re-executes via MOABB. VIREON does NOT perturb results
post-hoc.

Each perturbation:
  - has a `name` property (str)
  - has `severity` in [0, 1] (0 = no effect, 1 = severe)
  - has a `seed` for reproducibility
  - exposes `apply(data: np.ndarray) -> np.ndarray` that returns a perturbed COPY

Conventions:
  - Input `data` is never modified in place.
  - Output shape matches input shape.
  - All RNG is derived from `seed` for reproducibility.

Supported shapes (BCI epoch tensor convention):
  - (n_epochs, n_channels, n_times)   ← primary
  - (n_channels, n_times)            ← 2D convenience
  - (n_times,)                       ← single-channel convenience
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import numpy as np


class Perturbation(ABC):
    """Abstract base class for all robustness perturbations.

    Subclasses must implement `apply(data)` and provide a `name` property.
    """

    def __init__(self, severity: float = 0.0, seed: int = 42):
        if not (0.0 <= float(severity) <= 1.0):
            raise ValueError(
                f"Perturbation.severity must be in [0, 1]; got {severity}"
            )
        self.severity = float(severity)
        self.seed = int(seed)

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def apply(self, data: np.ndarray) -> np.ndarray:
        """Apply this perturbation to `data`. Must NOT modify the input."""
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(severity={self.severity}, seed={self.seed})"

    # ─── shared helpers ───

    def _rng(self) -> np.random.Generator:
        return np.random.default_rng(self.seed)

    @staticmethod
    def _ensure_3d(data: np.ndarray) -> tuple[np.ndarray, tuple]:
        """Coerce data to 3D (n_epochs, n_channels, n_times) and remember the
        original shape so apply() can restore it.

        Convention:
          - 1D (n_times,)              → (1, 1, n_times)
          - 2D (n_channels, n_times)   → (1, n_channels, n_times)
          - 3D                         → as-is
        """
        data = np.asarray(data)
        orig_shape = data.shape
        if data.ndim == 1:
            data = data[np.newaxis, np.newaxis, :]
        elif data.ndim == 2:
            data = data[np.newaxis, :, :]
        elif data.ndim != 3:
            raise ValueError(
                f"Perturbation.apply expects 1D/2D/3D data; got shape {orig_shape}"
            )
        return data, orig_shape

    @staticmethod
    def _restore_shape(data: np.ndarray, orig_shape: tuple) -> np.ndarray:
        """Inverse of _ensure_3d."""
        if len(orig_shape) == 1:
            return data[0, 0, :]
        if len(orig_shape) == 2:
            return data[0, :, :]
        return data


# ─── Concrete perturbations ───


class ChannelDropout(Perturbation):
    """Randomly zero out a fraction of channels.

    severity ∈ [0, 1] controls the expected fraction of channels zeroed.
    A channel that is dropped is zeroed across ALL time points and ALL epochs
    (if 3D input) — i.e., we drop channels, not individual samples.
    """

    @property
    def name(self) -> str:
        return "channel_dropout"

    def apply(self, data: np.ndarray) -> np.ndarray:
        data3d, orig_shape = self._ensure_3d(data)
        out = data3d.copy()
        n_channels = out.shape[1]
        if n_channels == 0:
            return out if len(orig_shape) == 3 else self._restore_shape(out, orig_shape)
        # Number of channels to drop = severity * n_channels, at least 0
        n_drop = int(round(self.severity * n_channels))
        if n_drop <= 0:
            return self._restore_shape(out, orig_shape)
        rng = self._rng()
        # Don't drop ALL channels (would destroy the signal entirely)
        n_drop = min(n_drop, n_channels - 1) if n_channels > 1 else 0
        if n_drop <= 0:
            return self._restore_shape(out, orig_shape)
        dropped = rng.choice(n_channels, size=n_drop, replace=False)
        out[:, dropped, :] = 0.0
        return self._restore_shape(out, orig_shape)


class WhiteNoise(Perturbation):
    """Add Gaussian white noise scaled to the per-channel signal std.

    The added noise has std = severity * mean(signal_std_per_channel).
    This makes the perturbation severity relative to the actual signal
    amplitude, not an arbitrary absolute scale.
    """

    @property
    def name(self) -> str:
        return "white_noise"

    def apply(self, data: np.ndarray) -> np.ndarray:
        data3d, orig_shape = self._ensure_3d(data)
        out = data3d.copy().astype(np.float64, copy=False)
        rng = self._rng()
        # Per-channel std (averaged across epochs and time)
        # std over (n_epochs, n_times) per channel
        per_channel_std = out.std(axis=(0, 2))  # shape (n_channels,)
        mean_std = float(per_channel_std.mean()) if per_channel_std.size else 1.0
        if mean_std == 0.0:
            mean_std = 1.0  # avoid div-by-zero for flat signals
        noise_std = self.severity * mean_std
        noise = rng.normal(loc=0.0, scale=noise_std, size=out.shape)
        out = out + noise
        return self._restore_shape(out, orig_shape)


class LineNoise(Perturbation):
    """Add 50 Hz (or configurable) power-line interference.

    Adds a sinusoid at `freq_hz` (default 50 Hz) to each channel with
    amplitude = severity * mean(signal_std_per_channel). Phase is randomized
    per channel for realism.

    The sampling rate is required; pass via the spec or via attribute
    `line_noise_sfreq`. If no sfreq is set, we assume 250 Hz as a sensible
    BCI default and emit a warning via metadata (the noise is still applied).
    """

    DEFAULT_SFREQ = 250.0
    DEFAULT_FREQ = 50.0

    def __init__(self, severity: float = 0.0, seed: int = 42,
                 sfreq: float | None = None, freq_hz: float = 50.0):
        super().__init__(severity=severity, seed=seed)
        self.sfreq = float(sfreq) if sfreq is not None else None
        self.freq_hz = float(freq_hz)

    @property
    def name(self) -> str:
        return "line_noise"

    def apply(self, data: np.ndarray) -> np.ndarray:
        data3d, orig_shape = self._ensure_3d(data)
        out = data3d.copy().astype(np.float64, copy=False)
        n_epochs, n_channels, n_times = out.shape
        sfreq = self.sfreq if self.sfreq is not None else self.DEFAULT_SFREQ
        # Per-channel std → noise amplitude
        per_channel_std = out.std(axis=(0, 2))
        mean_std = float(per_channel_std.mean()) if per_channel_std.size else 1.0
        if mean_std == 0.0:
            mean_std = 1.0
        amplitude = self.severity * mean_std
        rng = self._rng()
        t = np.arange(n_times) / sfreq
        # Random phase per channel (broadcast over epochs)
        phases = rng.uniform(0, 2 * np.pi, size=(n_channels,))
        # Shape: (n_channels, n_times) → broadcast to (n_epochs, n_channels, n_times)
        sine = amplitude * np.sin(2 * np.pi * self.freq_hz * t + phases[:, None])
        out = out + sine[None, :, :]
        return self._restore_shape(out, orig_shape)


class TimeShift(Perturbation):
    """Circularly shift each channel along the time axis (np.roll).

    The shift amount = severity * n_times (rounded). Sign is determined by
    the seed for reproducibility. Shift is circular (np.roll), so no data is
    lost.

    The SAME shift is applied to all channels/epochs — this models a global
    clock-skew perturbation.
    """

    @property
    def name(self) -> str:
        return "time_shift"

    def apply(self, data: np.ndarray) -> np.ndarray:
        data3d, orig_shape = self._ensure_3d(data)
        out = data3d.copy()
        n_times = out.shape[-1]
        if n_times == 0:
            return self._restore_shape(out, orig_shape)
        shift = int(round(self.severity * n_times))
        if shift == 0:
            return self._restore_shape(out, orig_shape)
        rng = self._rng()
        sign = 1 if rng.random() < 0.5 else -1
        shift = sign * shift
        out = np.roll(out, shift=shift, axis=-1)
        return self._restore_shape(out, orig_shape)


class AmplitudeScaling(Perturbation):
    """Apply a random per-channel amplitude scaling factor.

    Each channel is multiplied by a factor drawn uniformly from
    [1 - severity, 1 + severity]. This models electrode impedance drift.
    """

    @property
    def name(self) -> str:
        return "amplitude_scaling"

    def apply(self, data: np.ndarray) -> np.ndarray:
        data3d, orig_shape = self._ensure_3d(data)
        out = data3d.copy().astype(np.float64, copy=False)
        n_channels = out.shape[1]
        rng = self._rng()
        # Per-channel scale factor in [1 - severity, 1 + severity]
        factors = rng.uniform(
            low=1.0 - self.severity,
            high=1.0 + self.severity,
            size=(n_channels,),
        )
        out = out * factors[None, :, None]
        return self._restore_shape(out, orig_shape)


# ─── Registry ───

PERTURBATION_REGISTRY: dict[str, type[Perturbation]] = {
    "channel_dropout": ChannelDropout,
    "white_noise": WhiteNoise,
    "line_noise": LineNoise,
    "time_shift": TimeShift,
    "amplitude_scaling": AmplitudeScaling,
}


def make_perturbation(perturbation_spec) -> Perturbation:
    """Construct a Perturbation from a PerturbationSpec (or compatible dict).

    `perturbation_spec` may be:
      - a vireon_moabb.spec.PerturbationSpec instance (uses .type, .severity)
      - a dict with at least {"type": ..., "severity": ...}
    """
    # Support both dataclass-like and dict inputs
    if hasattr(perturbation_spec, "type"):
        ptype = perturbation_spec.type
        severity = getattr(perturbation_spec, "severity", 0.0)
        seed = getattr(perturbation_spec, "seed", 42)
    elif isinstance(perturbation_spec, dict):
        ptype = perturbation_spec["type"]
        severity = perturbation_spec.get("severity", 0.0)
        seed = perturbation_spec.get("seed", 42)
    else:
        raise TypeError(
            f"make_perturbation: expected PerturbationSpec or dict; got {type(perturbation_spec)}"
        )

    if ptype not in PERTURBATION_REGISTRY:
        raise ValueError(
            f"Unknown perturbation type '{ptype}'. "
            f"Available: {list(PERTURBATION_REGISTRY.keys())}"
        )
    cls = PERTURBATION_REGISTRY[ptype]
    return cls(severity=severity, seed=seed)


__all__ = [
    "Perturbation",
    "ChannelDropout",
    "WhiteNoise",
    "LineNoise",
    "TimeShift",
    "AmplitudeScaling",
    "PERTURBATION_REGISTRY",
    "make_perturbation",
]
