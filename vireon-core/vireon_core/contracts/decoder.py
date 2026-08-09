from abc import ABC, abstractmethod
import numpy as np

class DecoderNotFittedError(Exception):
    """Raised when predict or predict_proba is called before fit."""
    pass

class IDecoder(ABC):
    """
    Interface for BCI decoders in VIREON.
    """
    def __init__(self):
        self._fitted = False

    @abstractmethod
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """
        Train the decoder on epochs X with labels y.
        X shape: (n_epochs, n_channels, n_times)
        y shape: (n_epochs,)
        """
        self._fitted = True

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict labels for epochs X.
        Returns array of shape (n_epochs,)
        """
        if not getattr(self, '_fitted', False):
            raise DecoderNotFittedError("Decoder must be fitted before predict.")
        return np.array([])

    @abstractmethod
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict probabilities for epochs X.
        Returns array of shape (n_epochs, n_classes)
        """
        if not getattr(self, '_fitted', False):
            raise DecoderNotFittedError("Decoder must be fitted before predict_proba.")
        return np.array([])
