"""
VIREON × MOABB — Scientific Adapters.

Uniform wrapper around third-party scientific libraries (MOABB, MNE, sklearn,
scipy, pyriemann) so the validation and evidence layers can:

  - Identify which library produced a result (adapter_name).
  - Hash the result deterministically (execution_hash — SHA-256).
  - Dispatch operations by spec dict (ADR 0008 #4).

All adapters inherit from BaseAdapter and return AdapterResult.
"""
from vireon_moabb.adapters.base import BaseAdapter, AdapterResult, hash_bytes
from vireon_moabb.adapters.moabb_adapter import MoabbAdapter
from vireon_moabb.adapters.mne_adapter import MneAdapter
from vireon_moabb.adapters.sklearn_adapter import SklearnAdapter
from vireon_moabb.adapters.scipy_adapter import ScipyAdapter
from vireon_moabb.adapters.pyriemann_adapter import PyriemannAdapter

__all__ = [
    "BaseAdapter",
    "AdapterResult",
    "hash_bytes",
    "MoabbAdapter",
    "MneAdapter",
    "SklearnAdapter",
    "ScipyAdapter",
    "PyriemannAdapter",
]
