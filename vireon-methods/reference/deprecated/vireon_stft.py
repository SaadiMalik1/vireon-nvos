"""DEPRECATED: This native implementation is retained for reference only.
VIREON now delegates to mature libraries (MOABB, MNE, scipy, sklearn, pyriemann).
Use the corresponding adapter in vireon_moabb.adapters instead.

This file will be removed in v2.1.0.
"""
import numpy as np
from typing import Tuple
from vireon_core.contracts.plugin import ScientificContractViolation

class VireonSTFT:
    """Native Short-Time Fourier Transform (STFT) implementation.
    
    Produces a complex time-frequency representation of the signal.
    """
    
    def __init__(self, fs: float, nperseg: int = 256, noverlap: int = None,
                 window: str = "hann", detrend: str = "constant"):
        self.fs = fs
        self.nperseg = nperseg
        self.noverlap = noverlap if noverlap is not None else nperseg // 2
        self.window = window
        self.detrend = detrend
        
        if self.noverlap >= self.nperseg:
            raise ValueError("noverlap must be less than nperseg.")
            
    def compute(self, signal: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Returns (frequencies, times, Zxx) where Zxx is complex STFT."""
        if not isinstance(signal, np.ndarray):
            signal = np.array(signal)
            
        if np.any(np.isnan(signal)) or np.any(np.isinf(signal)):
            raise ScientificContractViolation(
                "Signal contains NaN or Inf values.",
                violated_assumption="finite_values",
                details="NaN or Inf detected.",
                remediation="Clean data."
            )
            
        if len(signal) < self.nperseg:
            raise ScientificContractViolation(
                f"Signal length {len(signal)} is smaller than nperseg {self.nperseg}.",
                violated_assumption="sufficient_length",
                details="Signal too short.",
                remediation="Provide longer signal."
            )
            
        # Get window coefficients (sym=False equivalent for scipy compatibility)
        if self.window == "hann":
            win = 0.5 - 0.5 * np.cos(2.0 * np.pi * np.arange(self.nperseg) / self.nperseg)
        else:
            win = np.ones(self.nperseg)
            
        step = self.nperseg - self.noverlap
        num_segments = (len(signal) - self.nperseg) // step + 1
        
        spectra = []
        win_sum = np.sum(win)
        
        for i in range(num_segments):
            start = i * step
            segment = signal[start:start + self.nperseg].copy()
            
            if self.detrend == "constant":
                segment -= np.mean(segment)
                
            fft_result = np.fft.rfft(segment * win)
            
            # Scipy STFT uses spectrum scaling by dividing by sum(window)
            fft_result = fft_result / win_sum
            
            spectra.append(fft_result)
            
        Zxx = np.stack(spectra, axis=1)
        freqs = np.fft.rfftfreq(self.nperseg, d=1/self.fs)
        times = (np.arange(num_segments) * step + self.nperseg / 2) / self.fs
        
        return freqs, times, Zxx
