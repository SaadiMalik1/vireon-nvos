"""
SklearnAdapter — wraps common sklearn operations behind the BaseAdapter contract.

Supported operations (selected via spec["operation"]):
    "fit_predict"      — fit an estimator, then predict on the same X (or on
                         X_test if provided). Returns predicted labels.
                         Required keys: estimator (class path "module.Class"),
                         params (dict), X (n_samples, n_features), y (labels),
                         optional X_test.
    "cross_val_score"  — Run sklearn.model_selection.cross_val_score.
                         Required keys: estimator, params, X, y, cv (int, default 5).
    "confusion_matrix" — Fit an estimator, predict, return sklearn confusion_matrix.
                         Required keys: estimator, params, X, y, optional X_test/y_test.

`estimator` may also be a pre-constructed sklearn estimator instance instead of
a "module.Class" string + params dict.
"""
from __future__ import annotations

import importlib
from typing import Any

import numpy as np

from vireon_moabb.adapters.base import BaseAdapter, AdapterResult, hash_bytes


class SklearnAdapter(BaseAdapter):
    """Adapter for sklearn fit / predict / cross-validation operations."""

    @property
    def name(self) -> str:
        return "sklearn"

    @property
    def library_version(self) -> str:
        return self._import_version("sklearn")

    def can_handle(self, spec: dict) -> bool:
        if not isinstance(spec, dict):
            return False
        op = spec.get("operation")
        return op in {"fit_predict", "cross_val_score", "confusion_matrix"}

    def execute(self, spec: dict, **kwargs) -> AdapterResult:
        op = spec.get("operation")
        if op == "fit_predict":
            return self._op_fit_predict(spec, **kwargs)
        if op == "cross_val_score":
            return self._op_cross_val_score(spec, **kwargs)
        if op == "confusion_matrix":
            return self._op_confusion_matrix(spec, **kwargs)
        raise ValueError(
            f"SklearnAdapter: unknown operation '{op}'. "
            f"Supported: fit_predict, cross_val_score, confusion_matrix"
        )

    # ─── estimator resolution ───

    def _resolve_estimator(self, spec: dict):
        """Resolve an estimator from `estimator` (instance or path string) +
        `params` dict in the spec."""
        estimator = spec.get("estimator")
        params = dict(spec.get("params", {}) or {})
        if estimator is None:
            raise ValueError("SklearnAdapter: spec['estimator'] is required")
        if isinstance(estimator, str):
            if "." not in estimator:
                raise ValueError(
                    f"SklearnAdapter: estimator string must be 'module.Class'; got '{estimator}'"
                )
            module_path, class_name = estimator.rsplit(".", 1)
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            return cls(**params)
        # Already an instance — ignore params (caller knows what they're doing)
        return estimator

    # ─── operations ───

    def _op_fit_predict(self, spec: dict, **kwargs) -> AdapterResult:
        X = np.asarray(spec["X"])
        y = np.asarray(spec["y"])
        X_test = spec.get("X_test")
        est = self._resolve_estimator(spec)
        est.fit(X, y)
        X_pred = np.asarray(X_test) if X_test is not None else X
        preds = est.predict(X_pred)

        execution_hash = hash_bytes(
            np.asarray(preds).tobytes(),
            str(np.asarray(preds).shape).encode(),
            str(np.asarray(preds).dtype).encode(),
        )

        metadata = {
            "adapter": self.name,
            "library_version": self.library_version,
            "operation": "fit_predict",
            "estimator": type(est).__name__,
            "n_train": int(len(X)),
            "n_predict": int(len(X_pred)),
            "n_classes": int(np.unique(y).size),
        }
        return AdapterResult(
            outputs={"predictions": preds, "estimator": est},
            metadata=metadata,
            execution_hash=execution_hash,
            adapter_name=self.name,
        )

    def _op_cross_val_score(self, spec: dict, **kwargs) -> AdapterResult:
        from sklearn.model_selection import cross_val_score

        X = np.asarray(spec["X"])
        y = np.asarray(spec["y"])
        cv = int(spec.get("cv", 5))
        est = self._resolve_estimator(spec)
        scores = cross_val_score(est, X, y, cv=cv)

        execution_hash = hash_bytes(
            np.asarray(scores).tobytes(),
            str(np.asarray(scores).shape).encode(),
        )

        metadata = {
            "adapter": self.name,
            "library_version": self.library_version,
            "operation": "cross_val_score",
            "estimator": type(est).__name__,
            "cv": cv,
            "n_samples": int(len(X)),
            "mean_score": float(np.mean(scores)),
            "std_score": float(np.std(scores)),
        }
        return AdapterResult(
            outputs={"scores": scores, "mean": float(np.mean(scores))},
            metadata=metadata,
            execution_hash=execution_hash,
            adapter_name=self.name,
        )

    def _op_confusion_matrix(self, spec: dict, **kwargs) -> AdapterResult:
        from sklearn.metrics import confusion_matrix as sk_confusion_matrix

        X = np.asarray(spec["X"])
        y = np.asarray(spec["y"])
        X_test = spec.get("X_test")
        y_test = spec.get("y_test")
        est = self._resolve_estimator(spec)
        est.fit(X, y)
        if X_test is not None and y_test is not None:
            preds = est.predict(np.asarray(X_test))
            true = np.asarray(y_test)
        else:
            preds = est.predict(X)
            true = y
        cm = sk_confusion_matrix(true, preds)

        execution_hash = hash_bytes(
            np.asarray(cm).tobytes(),
            str(np.asarray(cm).shape).encode(),
        )

        metadata = {
            "adapter": self.name,
            "library_version": self.library_version,
            "operation": "confusion_matrix",
            "estimator": type(est).__name__,
            "labels": list(np.unique(true).astype(int).tolist()),
            "shape": list(np.asarray(cm).shape),
        }
        return AdapterResult(
            outputs={"confusion_matrix": cm, "predictions": preds, "true": true},
            metadata=metadata,
            execution_hash=execution_hash,
            adapter_name=self.name,
        )
