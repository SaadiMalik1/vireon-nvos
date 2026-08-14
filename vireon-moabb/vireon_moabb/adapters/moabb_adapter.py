"""
MoabbAdapter — wraps MoabbExecutor behind the BaseAdapter contract.

This adapter is the bridge between VIREON's adapter layer and the existing
MoabbExecutor (which actually drives MOABB). VIREON validation code can
treat MOABB runs identically to MNE/sklearn runs: through a uniform
`AdapterResult` with a SHA-256 execution_hash.

Principle (ADR 0008 #4): VIREON may instrument execution. The MoabbExecutionTrace
captured by MoabbExecutor is the instrumented artifact; this adapter wraps it.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

from vireon_moabb.adapters.base import BaseAdapter, AdapterResult


class MoabbAdapter(BaseAdapter):
    """Adapter that runs an ExperimentSpec via MoabbExecutor."""

    def __init__(self, executor=None, seed: int = 42):
        """
        Args:
            executor: An existing MoabbExecutor instance. If None, a new one is
                created lazily on first execute() call (avoids importing MOABB
                until needed).
            seed: Seed for the MoabbExecutor if a new one is created.
        """
        self._executor = executor
        self._seed = seed

    # ─── BaseAdapter interface ───

    @property
    def name(self) -> str:
        return "moabb"

    @property
    def library_version(self) -> str:
        return self._import_version("moabb")

    def can_handle(self, spec: dict) -> bool:
        """Return True if `spec` looks like an ExperimentSpec dict."""
        if not isinstance(spec, dict):
            return False
        required = {"dataset", "paradigm", "pipeline", "evaluation"}
        return required.issubset(spec.keys())

    def execute(self, spec: dict, **kwargs) -> AdapterResult:
        """Run the ExperimentSpec via MoabbExecutor.

        Args:
            spec: An ExperimentSpec dict (or ExperimentSpec instance). Must
                contain dataset/paradigm/pipeline/evaluation sub-dicts.
            **kwargs: Ignored (kept for forward compatibility).

        Returns:
            AdapterResult with `outputs` set to the MoabbExecutionTrace,
            metadata recording moabb version / dataset / n_subjects / mean
            accuracy, and a SHA-256 execution_hash over the trace dict.
        """
        from vireon_moabb.spec import ExperimentSpec
        from vireon_moabb.executor import MoabbExecutor

        # Accept either a dict or an ExperimentSpec instance
        if isinstance(spec, dict):
            spec_obj = ExperimentSpec(**spec)
        else:
            spec_obj = spec

        executor = self._executor or MoabbExecutor(seed=self._seed)
        trace = executor.run(spec_obj)

        trace_dict = trace.to_dict()
        execution_hash = self._hash_trace(trace_dict)

        metadata = {
            "adapter": self.name,
            "library_version": self.library_version,
            "dataset_class": trace.dataset_metadata.dataset_class,
            "n_subjects": trace.dataset_metadata.n_subjects,
            "n_folds": len(trace.fold_results),
            "mean_accuracy": trace.mean_accuracy,
            "seed": trace.seed,
            "operation": "run_experiment",
        }

        return AdapterResult(
            outputs=trace,
            metadata=metadata,
            execution_hash=execution_hash,
            adapter_name=self.name,
        )

    # ─── internals ───

    @staticmethod
    def _hash_trace(trace_dict: dict[str, Any]) -> str:
        """SHA-256 over the JSON-serialized trace dict (sort_keys=True)."""
        # default=str tolerates datetimes, numpy types, etc.
        serial = json.dumps(trace_dict, sort_keys=True, default=str)
        return hashlib.sha256(serial.encode("utf-8")).hexdigest()
