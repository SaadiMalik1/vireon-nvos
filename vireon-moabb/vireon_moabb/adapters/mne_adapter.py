"""
MneAdapter — wraps common MNE operations behind the BaseAdapter contract.

Supported operations (selected via spec["operation"]):
    "filter"   — band-pass filter a 2D (n_channels, n_times) array.
                 Required keys: data, sfreq, l_freq, h_freq.
    "csp"      — fit/transform Common Spatial Patterns on epochs.
                 Required keys: X (n_epochs, n_channels, n_times), y (labels),
                                n_components (optional, default 4).
    "ica"      — fit ICA on a 2D array (n_channels, n_times) and return the
                 decomposed sources.
                 Required keys: data, sfreq, n_components (optional).

All operations return an AdapterResult with a SHA-256 hash over the output
bytes (and output shape/dtype where applicable).

The adapter NEVER modifies the input arrays in place — copies are taken.
"""
from __future__ import annotations

import copy
from typing import Any

import numpy as np

from vireon_moabb.adapters.base import BaseAdapter, AdapterResult, hash_bytes


class MneAdapter(BaseAdapter):
    """Adapter for MNE filtering / decoding / preprocessing operations."""

    @property
    def name(self) -> str:
        return "mne"

    @property
    def library_version(self) -> str:
        return self._import_version("mne")

    def can_handle(self, spec: dict) -> bool:
        if not isinstance(spec, dict):
            return False
        op = spec.get("operation")
        return op in {"filter", "csp", "ica"}

    def execute(self, spec: dict, **kwargs) -> AdapterResult:
        op = spec.get("operation")
        if op == "filter":
            return self._op_filter(spec, **kwargs)
        if op == "csp":
            return self._op_csp(spec, **kwargs)
        if op == "ica":
            return self._op_ica(spec, **kwargs)
        raise ValueError(
            f"MneAdapter: unknown operation '{op}'. "
            f"Supported: filter, csp, ica"
        )

    # ─── operations ───

    def _op_filter(self, spec: dict, **kwargs) -> AdapterResult:
        import mne

        data = np.asarray(spec["data"], dtype=np.float64)
        sfreq = float(spec["sfreq"])
        l_freq = spec.get("l_freq")
        h_freq = spec.get("h_freq")

        # Build a RawArray (MNE expects (n_channels, n_times))
        if data.ndim != 2:
            raise ValueError(
                f"MneAdapter.filter expects 2D (n_channels, n_times); got shape {data.shape}"
            )
        info = mne.create_info(
            ch_names=[f"ch{i}" for i in range(data.shape[0])],
            sfreq=sfreq,
            ch_types="eeg",
        )
        raw = mne.io.RawArray(copy.deepcopy(data), info, verbose=False)
        raw.filter(l_freq, h_freq, verbose=False)
        filtered = raw.get_data()

        execution_hash = hash_bytes(filtered.tobytes(), str(filtered.shape).encode(),
                                   str(filtered.dtype).encode())

        metadata = {
            "adapter": self.name,
            "library_version": self.library_version,
            "operation": "filter",
            "sfreq": sfreq,
            "l_freq": l_freq,
            "h_freq": h_freq,
            "input_shape": list(data.shape),
            "output_shape": list(filtered.shape),
        }
        return AdapterResult(
            outputs=filtered,
            metadata=metadata,
            execution_hash=execution_hash,
            adapter_name=self.name,
        )

    def _op_csp(self, spec: dict, **kwargs) -> AdapterResult:
        from mne.decoding import CSP

        X = np.asarray(spec["X"], dtype=np.float64)
        y = np.asarray(spec["y"])
        n_components = int(spec.get("n_components", 4))

        if X.ndim != 3:
            raise ValueError(
                f"MneAdapter.csp expects 3D (n_epochs, n_channels, n_times); got shape {X.shape}"
            )
        csp = CSP(n_components=n_components, log=False, norm_trace=False)
        features = csp.fit_transform(X, y)

        execution_hash = hash_bytes(
            features.tobytes(),
            str(features.shape).encode(),
            str(features.dtype).encode(),
            np.asarray(csp.filters_).tobytes() if hasattr(csp, "filters_") else b"<nofilters>",
        )

        metadata = {
            "adapter": self.name,
            "library_version": self.library_version,
            "operation": "csp",
            "n_components": n_components,
            "n_epochs": int(X.shape[0]),
            "n_channels": int(X.shape[1]),
            "n_times": int(X.shape[2]),
            "n_classes": int(np.unique(y).size),
            "output_shape": list(features.shape),
        }
        return AdapterResult(
            outputs={"features": features, "filters": csp.filters_},
            metadata=metadata,
            execution_hash=execution_hash,
            adapter_name=self.name,
        )

    def _op_ica(self, spec: dict, **kwargs) -> AdapterResult:
        from mne.preprocessing import ICA

        data = np.asarray(spec["data"], dtype=np.float64)
        sfreq = float(spec["sfreq"])
        n_components = int(spec.get("n_components", data.shape[0]))

        if data.ndim != 2:
            raise ValueError(
                f"MneAdapter.ica expects 2D (n_channels, n_times); got shape {data.shape}"
            )
        import mne
        info = mne.create_info(
            ch_names=[f"ch{i}" for i in range(data.shape[0])],
            sfreq=sfreq,
            ch_types="eeg",
        )
        raw = mne.io.RawArray(copy.deepcopy(data), info, verbose=False)
        ica = ICA(n_components=min(n_components, data.shape[0]), random_state=42, verbose=False)
        ica.fit(raw)
        sources = ica.get_sources(raw).get_data()

        execution_hash = hash_bytes(
            sources.tobytes(),
            str(sources.shape).encode(),
            str(sources.dtype).encode(),
            np.asarray(ica.mixing_matrix_).tobytes() if hasattr(ica, "mixing_matrix_") else b"<nomixing>",
        )

        metadata = {
            "adapter": self.name,
            "library_version": self.library_version,
            "operation": "ica",
            "n_components": int(ica.n_components),
            "sfreq": sfreq,
            "input_shape": list(data.shape),
            "output_shape": list(sources.shape),
        }
        return AdapterResult(
            outputs={"sources": sources, "mixing_matrix": getattr(ica, "mixing_matrix_", None)},
            metadata=metadata,
            execution_hash=execution_hash,
            adapter_name=self.name,
        )
