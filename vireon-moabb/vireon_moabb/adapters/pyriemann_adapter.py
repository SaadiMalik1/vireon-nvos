"""
PyriemannAdapter — wraps pyriemann operations behind the BaseAdapter contract.

Supported operations (selected via spec["operation"]):
    "covariances"     — Estimate covariance matrices via pyriemann.estimation.Covariances.
                        Required keys: X (n_epochs, n_channels, n_times).
                        Optional: estimator (default 'oas').
    "tangent_space"   — Project covariance matrices to tangent space via
                        pyriemann.tangentspace.TangentSpace.
                        Required keys: X (n_epochs, n_channels, n_channels) — covariance matrices.
                        Optional: tsquare (bool, default False).
    "mdm"             — Minimum Distance to Mean classifier.
                        Required keys: X (covariances), y (labels).
                        Optional: metric (default 'riemann').

pyriemann is an OPTIONAL dependency — all imports are lazy. If pyriemann is
not installed, instantiating the adapter still works, but execute() raises
a clear ImportError. can_handle() returns True regardless (the spec is
structurally valid; only execution requires pyriemann).
"""
from __future__ import annotations

from typing import Any

import numpy as np

from vireon_moabb.adapters.base import BaseAdapter, AdapterResult, hash_bytes


class PyriemannAdapter(BaseAdapter):
    """Adapter for pyriemann covariance / tangent-space / MDM operations."""

    @property
    def name(self) -> str:
        return "pyriemann"

    @property
    def library_version(self) -> str:
        return self._import_version("pyriemann")

    def can_handle(self, spec: dict) -> bool:
        if not isinstance(spec, dict):
            return False
        op = spec.get("operation")
        return op in {"covariances", "tangent_space", "mdm"}

    def execute(self, spec: dict, **kwargs) -> AdapterResult:
        op = spec.get("operation")
        if op == "covariances":
            return self._op_covariances(spec, **kwargs)
        if op == "tangent_space":
            return self._op_tangent_space(spec, **kwargs)
        if op == "mdm":
            return self._op_mdm(spec, **kwargs)
        raise ValueError(
            f"PyriemannAdapter: unknown operation '{op}'. "
            f"Supported: covariances, tangent_space, mdm"
        )

    # ─── operations ───

    def _op_covariances(self, spec: dict, **kwargs) -> AdapterResult:
        try:
            from pyriemann.estimation import Covariances
        except ImportError as e:
            raise ImportError(
                "PyriemannAdapter.covariances requires the 'pyriemann' package. "
                "Install via: pip install pyriemann"
            ) from e

        X = np.asarray(spec["X"], dtype=np.float64)
        estimator = spec.get("estimator", "oas")
        cov = Covariances(estimator=estimator)
        cov_mats = cov.transform(X)

        execution_hash = hash_bytes(
            np.asarray(cov_mats).tobytes(),
            str(np.asarray(cov_mats).shape).encode(),
            str(np.asarray(cov_mats).dtype).encode(),
        )
        metadata = {
            "adapter": self.name,
            "library_version": self.library_version,
            "operation": "covariances",
            "estimator": estimator,
            "input_shape": list(X.shape),
            "output_shape": list(np.asarray(cov_mats).shape),
        }
        return AdapterResult(
            outputs={"covariances": cov_mats, "estimator_object": cov},
            metadata=metadata,
            execution_hash=execution_hash,
            adapter_name=self.name,
        )

    def _op_tangent_space(self, spec: dict, **kwargs) -> AdapterResult:
        try:
            from pyriemann.tangentspace import TangentSpace
        except ImportError as e:
            raise ImportError(
                "PyriemannAdapter.tangent_space requires the 'pyriemann' package. "
                "Install via: pip install pyriemann"
            ) from e

        X = np.asarray(spec["X"], dtype=np.float64)
        tsquare = bool(spec.get("tsquare", False))
        ts = TangentSpace(tsquare=tsquare)
        if "y" in spec and spec["y"] is not None:
            features = ts.fit_transform(X, np.asarray(spec["y"]))
        else:
            features = ts.fit_transform(X)

        execution_hash = hash_bytes(
            np.asarray(features).tobytes(),
            str(np.asarray(features).shape).encode(),
            str(np.asarray(features).dtype).encode(),
        )
        metadata = {
            "adapter": self.name,
            "library_version": self.library_version,
            "operation": "tangent_space",
            "tsquare": tsquare,
            "input_shape": list(X.shape),
            "output_shape": list(np.asarray(features).shape),
        }
        return AdapterResult(
            outputs={"features": features, "estimator_object": ts},
            metadata=metadata,
            execution_hash=execution_hash,
            adapter_name=self.name,
        )

    def _op_mdm(self, spec: dict, **kwargs) -> AdapterResult:
        try:
            from pyriemann.classification import MDM
        except ImportError as e:
            raise ImportError(
                "PyriemannAdapter.mdm requires the 'pyriemann' package. "
                "Install via: pip install pyriemann"
            ) from e

        X = np.asarray(spec["X"], dtype=np.float64)
        y = np.asarray(spec["y"])
        metric = spec.get("metric", "riemann")
        mdm = MDM(metric=metric)
        mdm.fit(X, y)
        preds = mdm.predict(X)

        execution_hash = hash_bytes(
            np.asarray(preds).tobytes(),
            str(np.asarray(preds).shape).encode(),
            str(np.asarray(preds).dtype).encode(),
        )
        metadata = {
            "adapter": self.name,
            "library_version": self.library_version,
            "operation": "mdm",
            "metric": metric,
            "n_samples": int(len(X)),
            "n_classes": int(np.unique(y).size),
        }
        return AdapterResult(
            outputs={"predictions": preds, "estimator_object": mdm},
            metadata=metadata,
            execution_hash=execution_hash,
            adapter_name=self.name,
        )
