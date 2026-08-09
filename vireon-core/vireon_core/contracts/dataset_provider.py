from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
import numpy as np

class IDatasetProvider(ABC):
    """
    Interface for Dataset Providers.
    Dataset providers are higher-level abstractions that load a specific 
    public dataset and return standardized attributes (Raw, events, metadata).
    """
    @abstractmethod
    def load(self, subject: int, run: int) -> Tuple[Any, np.ndarray, Dict[str, Any]]:
        """
        Loads the dataset for a given subject and run.
        Returns:
            raw: MNE Raw object (or equivalent)
            events: np.ndarray of events
            metadata: dict of dataset-specific metadata
        """
        pass
