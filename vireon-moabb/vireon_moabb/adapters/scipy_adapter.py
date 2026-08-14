"""
ScipyAdapter — wraps scipy.signal operations behind the BaseAdapter contract.

Supported operations (selected via spec["operation"]):
    "welch"      — Power spectral density via Welch's method.
                   Required keys: data (1D or 2D (n_channels, n_times)), fs (sample rate).
                   Optional: nperseg, noverlap, nfft.
    "periodogram" — Power spectral density via periodogram.
                   Required keys: data, fs.
                   Optional: nfft, window.
    "stft"       — Short-time Fourier transform.
                   Required keys: data, fs.
                   Optional: nperseg, noverlap, nfft.
    "csd"        — Cross spectral density between two signals.
                   Required keys: data (2D, shape (2, n_times)) OR (x, y) keys, fs.

All operations return an AdapterResult with a SHA-256 hash over the output
bytes (frequencies array + psd/stft array).
"""
from __future__ import annotations

from typing import Any

import numpy as np

from vireon_moabb.adapters.base import BaseAdapter, AdapterResult, hash_bytes


class ScipyAdapter(BaseAdapter):
    """Adapter for scipy.signal spectral / time-frequency operations."""

    @property
    def name(self) -> str:
        return "scipy"

    @property
    def library_version(self) -> str:
        return self._import_version("scipy")

    def can_handle(self, spec: dict) -> bool:
        if not isinstance(spec, dict):
            return False
        op = spec.get("operation")
        return op in {"welch", "periodogram", "stft", "csd"}

    def execute(self, spec: dict, **kwargs) -> AdapterResult:
        op = spec.get("operation")
        if op == "welch":
            return self._op_welch(spec, **kwargs)
        if op == "periodogram":
            return self._op_periodogram(spec, **kwargs)
        if op == "stft":
            return self._op_stft(spec, **kwargs)
        if op == "csd":
            return self._op_csd(spec, **kwargs)
        raise ValueError(
            f"ScipyAdapter: unknown operation '{op}'. "
            f"Supported: welch, periodogram, stft, csd"
        )

    # ─── helpers ───

    def _common_kwargs(self, spec: dict) -> dict:
        """Extract the common scipy.signal kwargs from the spec."""
        out = {}
        for k in ("nperseg", "noverlap", "nfft", "window", "detrend", "scaling"):
            if k in spec:
                out[k] = spec[k]
        return out

    def _hash_spectral(self, freqs: np.ndarray, psd: np.ndarray) -> str:
        return hash_bytes(
            np.asarray(freqs).tobytes(),
            np.asarray(psd).tobytes(),
            str(np.asarray(freqs).shape).encode(),
            str(np.asarray(psd).shape).encode(),
            str(np.asarray(psd).dtype).encode(),
        )

    # ─── operations ───

    def _op_welch(self, spec: dict, **kwargs) -> AdapterResult:
        from scipy.signal import welch

        data = np.asarray(spec["data"])
        fs = float(spec["fs"])
        extra = self._common_kwargs(spec)
        freqs, psd = welch(data, fs=fs, **extra)

        execution_hash = self._hash_spectral(freqs, psd)
        metadata = {
            "adapter": self.name,
            "library_version": self.library_version,
            "operation": "welch",
            "fs": fs,
            "input_shape": list(data.shape),
            "freqs_shape": list(np.asarray(freqs).shape),
            "psd_shape": list(np.asarray(psd).shape),
        }
        return AdapterResult(
            outputs={"freqs": freqs, "psd": psd},
            metadata=metadata,
            execution_hash=execution_hash,
            adapter_name=self.name,
        )

    def _op_periodogram(self, spec: dict, **kwargs) -> AdapterResult:
        from scipy.signal import periodogram

        data = np.asarray(spec["data"])
        fs = float(spec["fs"])
        extra = self._common_kwargs(spec)
        freqs, psd = periodogram(data, fs=fs, **extra)

        execution_hash = self._hash_spectral(freqs, psd)
        metadata = {
            "adapter": self.name,
            "library_version": self.library_version,
            "operation": "periodogram",
            "fs": fs,
            "input_shape": list(data.shape),
            "freqs_shape": list(np.asarray(freqs).shape),
            "psd_shape": list(np.asarray(psd).shape),
        }
        return AdapterResult(
            outputs={"freqs": freqs, "psd": psd},
            metadata=metadata,
            execution_hash=execution_hash,
            adapter_name=self.name,
        )

    def _op_stft(self, spec: dict, **kwargs) -> AdapterResult:
        from scipy.signal import stft

        data = np.asarray(spec["data"])
        fs = float(spec["fs"])
        extra = self._common_kwargs(spec)
        freqs, times, Z = stft(data, fs=fs, **extra)

        execution_hash = hash_bytes(
            np.asarray(freqs).tobytes(),
            np.asarray(times).tobytes(),
            np.asarray(Z).tobytes(),
            str(np.asarray(Z).shape).encode(),
            str(np.asarray(Z).dtype).encode(),
        )
        metadata = {
            "adapter": self.name,
            "library_version": self.library_version,
            "operation": "stft",
            "fs": fs,
            "input_shape": list(data.shape),
            "freqs_shape": list(np.asarray(freqs).shape),
            "times_shape": list(np.asarray(times).shape),
            "Z_shape": list(np.asarray(Z).shape),
        }
        return AdapterResult(
            outputs={"freqs": freqs, "times": times, "Z": Z},
            metadata=metadata,
            execution_hash=execution_hash,
            adapter_name=self.name,
        )

    def _op_csd(self, spec: dict, **kwargs) -> AdapterResult:
        from scipy.signal import csd

        if "x" in spec and "y" in spec:
            x = np.asarray(spec["x"])
            y = np.asarray(spec["y"])
        else:
            data = np.asarray(spec["data"])
            if data.ndim != 2 or data.shape[0] != 2:
                raise ValueError(
                    "ScipyAdapter.csd: spec['data'] must be shape (2, n_times) "
                    "OR spec must contain 'x' and 'y' arrays"
                )
            x, y = data[0], data[1]
        fs = float(spec["fs"])
        extra = self._common_kwargs(spec)
        freqs, Pxy = csd(x, y, fs=fs, **extra)

        execution_hash = self._hash_spectral(freqs, Pxy)
        metadata = {
            "adapter": self.name,
            "library_version": self.library_version,
            "operation": "csd",
            "fs": fs,
            "n_times": int(len(x)),
            "freqs_shape": list(np.asarray(freqs).shape),
            "csd_shape": list(np.asarray(Pxy).shape),
        }
        return AdapterResult(
            outputs={"freqs": freqs, "csd": Pxy},
            metadata=metadata,
            execution_hash=execution_hash,
            adapter_name=self.name,
        )
