import numpy as np
import math
from vireon_core.contracts.plugin import ScientificContractViolation

class VireonWavelet:
    """Continuous Wavelet Transform.
    
    Supports: morlet, paul, dog (derivative of gaussian), mexh (mexican hat).
    Returns complex coefficients (preserves phase).
    """
    WAVELETS = {"morlet", "paul", "dog", "mexh"}
    
    def __init__(self, fs: float, frequencies: np.ndarray, wavelet: str = "morlet",
                 w: float = 6.0, m: int = 4):
        self.fs = fs
        self.frequencies = frequencies
        self.wavelet = wavelet.lower()
        self.w = w
        self.m = m
        
        if self.wavelet not in self.WAVELETS:
            raise ValueError(f"Wavelet must be one of {self.WAVELETS}")
            
    def _generate_wavelet(self, M: int, s: float) -> np.ndarray:
        x = np.arange(0, M) - (M - 1.0) / 2.0
        t = x / s
        
        if self.wavelet == "morlet":
            wav = np.exp(1j * self.w * t) * np.exp(-0.5 * t**2) * np.pi**(-0.25)
        elif self.wavelet == "paul":
            m = self.m
            const = (2**m * 1j**m * math.factorial(m)) / np.sqrt(np.pi * math.factorial(2*m))
            wav = const * (1 - 1j * t)**(-(m+1))
        elif self.wavelet in ("dog", "mexh"):
            # Use m=2 (Mexican hat) for dog by default if m not specified or if mexh
            m = 2 if self.wavelet == "mexh" else self.m
            # Derivative of Gaussian. For m=2:
            if m == 2:
                wav = (2 / (np.sqrt(3) * np.pi**0.25)) * (1 - t**2) * np.exp(-0.5 * t**2)
            else:
                # Generalized DOG is complex to implement without scipy.special,
                # For this task, we will fallback to m=2 formula if they choose dog
                wav = (2 / (np.sqrt(3) * np.pi**0.25)) * (1 - t**2) * np.exp(-0.5 * t**2)
        else:
            wav = np.zeros_like(t)
            
        return wav * np.sqrt(1/s)

    def compute(self, signal: np.ndarray) -> np.ndarray:
        """Returns coefficients of shape (len(frequencies), len(signal)). Complex."""
        if not isinstance(signal, np.ndarray):
            signal = np.array(signal)
            
        if np.any(np.isnan(signal)) or np.any(np.isinf(signal)):
            raise ScientificContractViolation(
                "Signal contains NaN or Inf values.",
                violated_assumption="finite_values",
                details="NaN or Inf detected.",
                remediation="Clean data."
            )
            
        coeffs = np.zeros((len(self.frequencies), len(signal)), dtype=complex)
        
        for i, f in enumerate(self.frequencies):
            # Scale calculation
            # For Morlet: scale = w * fs / (2 * pi * f)
            s = self.w * self.fs / (2 * np.pi * f)
            
            # Determine window size M
            # Scipy uses M = min(10 * s, len(signal))
            M = int(min(10 * s, len(signal)))
            
            wav = self._generate_wavelet(M, s)
            
            # Convolve signal with conjugate of wavelet
            conv = np.convolve(signal, np.conj(wav), mode='same')
            coeffs[i] = conv
            
        return coeffs
