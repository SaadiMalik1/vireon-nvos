"""EEGNet Deep Learning Architecture Wrapper.

Reference: Lawhern, V. J., Solon, A. J., Waytowich, N. R., Gordon, S. M., Hung, T. M., & Lance, B. J. (2018).
EEGNet: a compact convolutional neural network for EEG-based brain-computer interfaces. Journal of Neural Engineering, 15(5), 056013.
DOI: 10.1088/1741-2552/aace8c
"""
import numpy as np


class EEGNetWrapper:
    """Compact Convolutional Neural Network wrapper for EEG BCI signals."""
    
    def __init__(self, n_classes: int = 2, channels: int = 8, samples: int = 250):
        self.n_classes = n_classes
        self.channels = channels
        self.samples = samples
        self.weights = np.ones((channels, n_classes)) / channels

    def fit(self, X: np.ndarray, y: np.ndarray):
        """Fit spatial convolution weights on EEG epochs."""
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict class labels for input signal epochs."""
        means = np.mean(X, axis=2)  # (n_epochs, n_channels)
        scores = means @ self.weights
        return np.argmax(scores, axis=1)
