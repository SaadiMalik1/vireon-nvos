"""
BaseAdapter — abstract contract for VIREON's scientific adapters.

Adapters wrap third-party libraries (MOABB, MNE, sklearn, scipy, pyriemann)
behind a uniform interface so the validation / evidence layers can:
- Inspect what library produced a result
- Hash the output for provenance (ADR 0008 #7)
- Dispatch operations based on a spec dict (ADR 0008 #4)

The adapters do NOT own BCI semantics. They are thin, hashable wrappers.
"""
from __future__ import annotations

import hashlib
import importlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AdapterResult:
    """Uniform output of every adapter.execute() call.

    Fields:
        outputs: The primary output object(s) of the operation (ndarray, dict,
            trace, etc.). Type varies per adapter / operation.
        metadata: Free-form dict of provenance — library name/version, operation
            name, parameters used, output shape, etc.
        execution_hash: SHA-256 hex digest over a stable serialization of the
            outputs (and key metadata). Tampering with outputs breaks the hash.
        adapter_name: Name of the adapter that produced this result.
    """
    outputs: Any
    metadata: dict[str, Any] = field(default_factory=dict)
    execution_hash: str = ""
    adapter_name: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Best-effort serialization for hashing / logging."""
        return {
            "adapter_name": self.adapter_name,
            "metadata": self.metadata,
            "execution_hash": self.execution_hash,
            "outputs_type": type(self.outputs).__name__,
        }


def hash_bytes(*buffers: bytes) -> str:
    """Compute a SHA-256 hex digest over one or more byte buffers.

    Used by adapters to derive `execution_hash` deterministically.
    """
    h = hashlib.sha256()
    for buf in buffers:
        if buf is None:
            h.update(b"<none>")
            continue
        if isinstance(buf, str):
            h.update(buf.encode("utf-8"))
        elif isinstance(buf, (bytes, bytearray, memoryview)):
            h.update(bytes(buf))
        else:
            # Fallback: numpy array or picklable object
            try:
                import numpy as np
                if isinstance(buf, np.ndarray):
                    h.update(buf.tobytes())
                    h.update(str(buf.shape).encode("utf-8"))
                    h.update(str(buf.dtype).encode("utf-8"))
                    continue
            except Exception:
                pass
            import pickle
            h.update(pickle.dumps(buf))
    return h.hexdigest()


class BaseAdapter(ABC):
    """Abstract base class for all VIREON scientific adapters.

    Subclasses must implement:
        name -> str
        library_version -> str
        can_handle(spec) -> bool
        execute(spec, **kwargs) -> AdapterResult
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Short, human-readable adapter identifier (e.g. 'mne')."""
        raise NotImplementedError

    @property
    @abstractmethod
    def library_version(self) -> str:
        """Version string of the wrapped library, or 'unknown' if unavailable."""
        raise NotImplementedError

    @abstractmethod
    def can_handle(self, spec: dict) -> bool:
        """Return True iff this adapter is capable of executing the given spec."""
        raise NotImplementedError

    @abstractmethod
    def execute(self, spec: dict, **kwargs) -> AdapterResult:
        """Execute the operation described by `spec` and return an AdapterResult."""
        raise NotImplementedError

    # ─── helpers available to subclasses ───

    @staticmethod
    def _import_version(module_name: str) -> str:
        """Best-effort import of a library version string."""
        try:
            mod = importlib.import_module(module_name)
            return getattr(mod, "__version__", "unknown")
        except Exception:
            return "unknown"
