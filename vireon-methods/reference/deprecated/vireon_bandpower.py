"""DEPRECATED: This native implementation is retained for reference only.
VIREON now delegates to mature libraries (MOABB, MNE, scipy, sklearn, pyriemann).
Use the corresponding adapter in vireon_moabb.adapters instead.

This file will be removed in v2.1.0.
"""
import numpy as np
from scipy import signal
from typing import Tuple, Dict

class VireonBandpower:
    """
    Computes absolute and relative band power from continuous or epoched signals.
    """
    DEFAULT_BANDS = {
        "delta": (0.5, 4.0),
        "theta": (4.0, 8.0),
        "alpha": (8.0, 13.0),
        "beta": (13.0, 30.0),
        "gamma": (30.0, 50.0),
    }

    def __init__(self, fs: float, bands: Dict[str, Tuple[float, float]] = None):
        self.fs = fs
        self.bands = bands or self.DEFAULT_BANDS

    def compute(self, data: np.ndarray) -> Dict[str, float]:
        """
        Calculates average band power across channels.
        """
        freqs, psd = signal.welch(data, fs=self.fs, axis=-1)
        freq_res = freqs[1] - freqs[0]
        
        band_powers = {}
        for band, (low, high) in self.bands.items():
            idx = np.logical_and(freqs >= low, freqs <= high)
            bp = np.sum(psd[..., idx], axis=-1) * freq_res
            band_powers[band] = float(np.mean(bp))
            
        return band_powers
