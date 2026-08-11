"""DEPRECATED: This native implementation is retained for reference only.
VIREON now delegates to mature libraries (MOABB, MNE, scipy, sklearn, pyriemann).
Use the corresponding adapter in vireon_moabb.adapters instead.

This file will be removed in v2.1.0.
"""
import numpy as np
from typing import Tuple
from vireon_core.contracts.plugin import ScientificContractViolation

class VireonFFT:
    """Native FFT / periodogram implementation.
    
    Supports:
    - Real FFT (rfft for real-valued signals)
    - Windowing (hann, hamming, blackman, boxcar)
    - One-sided spectrum scaling (x2 for non-DC, non-Nyquist bins)
    - Power spectrum (V^2) and power spectral density (V^2/Hz)
    """
    
    def __init__(self, fs: float, nfft: int = None, window: str = "hann",
                 detrend: str = "constant", scaling: str = "density"):
        self.fs = fs
        self.nfft = nfft
        self.window = window
        self.detrend = detrend
        self.scaling = scaling
        
    def _prepare_signal_and_window(self, signal: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        if not isinstance(signal, np.ndarray):
            signal = np.array(signal)
            
        if np.any(np.isnan(signal)) or np.any(np.isinf(signal)):
            raise ScientificContractViolation(
                "Signal contains NaN or Inf values.",
                violated_assumption="finite_values",
                details="NaN or Inf detected.",
                remediation="Clean data."
            )
            
        N = len(signal)
        nfft = self.nfft if self.nfft is not None else N
        
        if self.detrend == "constant":
            signal = signal - np.mean(signal)
            
        if self.window == "hann":
            win = 0.5 - 0.5 * np.cos(2.0 * np.pi * np.arange(N) / N)
        elif self.window == "boxcar":
            win = np.ones(N)
        elif self.window == "hamming":
            win = 0.54 - 0.46 * np.cos(2.0 * np.pi * np.arange(N) / N)
        elif self.window == "blackman":
            win = 0.42 - 0.5 * np.cos(2.0 * np.pi * np.arange(N) / N) + 0.08 * np.cos(4.0 * np.pi * np.arange(N) / N)
        else:
            win = np.ones(N)
            
        return signal * win, win, nfft
        
    def compute(self, signal: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Returns (frequencies, psd)"""
        windowed, win, nfft = self._prepare_signal_and_window(signal)
        
        fft_result = np.fft.rfft(windowed, n=nfft)
        
        U = np.sum(win**2) if self.scaling == "density" else (np.sum(win))**2
        
        Pxx = np.abs(fft_result)**2
        if self.scaling == "density":
            Pxx /= (self.fs * U)
        else:
            Pxx /= U
            
        if len(Pxx) > 2:
            if nfft % 2 == 0:
                Pxx[1:-1] *= 2
            else:
                Pxx[1:] *= 2
                
        freqs = np.fft.rfftfreq(nfft, d=1/self.fs)
        return freqs, Pxx

    def compute_magnitude_spectrum(self, signal: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Returns (frequencies, |FFT|)"""
        windowed, _, nfft = self._prepare_signal_and_window(signal)
        fft_result = np.fft.rfft(windowed, n=nfft)
        mag = np.abs(fft_result)
        
        # Similar to scipy, we normalize magnitude spectrum by sum of window?
        # The prompt says: compute_magnitude_spectrum returns linear magnitudes.
        # So |FFT|. No scaling or one-sided scaling was explicitly required, but 
        # normally magnitude spectrum is scaled by 2/sum(window) if it represents 
        # physical amplitudes. The prompt just says returns |FFT|.
        
        freqs = np.fft.rfftfreq(nfft, d=1/self.fs)
        return freqs, mag
        
    def compute_phase_spectrum(self, signal: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Returns (frequencies, angle(FFT))"""
        windowed, _, nfft = self._prepare_signal_and_window(signal)
        fft_result = np.fft.rfft(windowed, n=nfft)
        phase = np.angle(fft_result)
        
        freqs = np.fft.rfftfreq(nfft, d=1/self.fs)
        return freqs, phase
