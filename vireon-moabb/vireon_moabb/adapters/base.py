from abc import ABC, abstractmethod
from typing import Any, Optional
from dataclasses import dataclass


@dataclass
class AdapterResult:
    """Result from an adapter execution."""
    outputs: Any
    metadata: dict
    execution_hash: str
    adapter_name: str


class BaseAdapter(ABC):
    """Base class for scientific library adapters.

    Each adapter wraps a specific library (MOABB, MNE, scipy, etc.)
    and provides a uniform interface for VIREON to execute and instrument.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Adapter name (e.g., 'moabb', 'mne', 'scipy')."""
        pass

    @property
    @abstractmethod
    def library_version(self) -> str:
        """Version of the underlying library."""
        pass

    @abstractmethod
    def execute(self, spec: dict, **kwargs) -> AdapterResult:
        """Execute the specified operation.

        Args:
            spec: Operation specification (varies by adapter).
            **kwargs: Additional parameters.

        Returns:
            AdapterResult with outputs, metadata, and execution hash.
        """
        pass

    @abstractmethod
    def can_handle(self, spec: dict) -> bool:
        """Check if this adapter can handle the given spec."""
        pass
