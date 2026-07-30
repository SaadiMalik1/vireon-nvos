from abc import ABC, abstractmethod
from typing import Any, Dict, List
import numpy as np

class IDecoder(ABC):
    """
    Interface for BCI decoders in VIREON.
    """
    @abstractmethod
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        Train the decoder on epochs X with labels y.
        X shape: (n_epochs, n_channels, n_times)
        y shape: (n_epochs,)
        """
        pass

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict labels for epochs X.
        Returns array of shape (n_epochs,)
        """
        pass

    @abstractmethod
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict probabilities for epochs X.
        Returns array of shape (n_epochs, n_classes)
        """
        pass
