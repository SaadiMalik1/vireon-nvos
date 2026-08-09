import numpy as np
from typing import Tuple
from vireon_core.contracts.plugin import ScientificContractViolation

class VireonWelch:
    """Native Welch PSD implementation.
    
    Reference: Welch, P. D. (1967). The Use of Fast Fourier Transform for the 
    Estimation of Power Spectra: A Method Based on Time Averaging Over Short, 
    Modified Periodograms. IEEE Transactions on Audio and Electroacoustics, 15(2), 70–73.
    DOI: 10.1109/TAU.1967.1161901
    """
    
    def __init__(self, fs: float, nperseg: int = 256, noverlap: int = None, 
                 window: str = "hann", detrend: str = "constant", 
                 scaling: str = "density"):
        self.fs = fs
        self.nperseg = nperseg
        self.noverlap = noverlap if noverlap is not None else nperseg // 2
        self.window = window
        self.detrend = detrend
        self.scaling = scaling
        
    def compute(self, signal: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
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
            
        # Get window coefficients
        if self.window == "hann":
            win = 0.5 - 0.5 * np.cos(2.0 * np.pi * np.arange(self.nperseg) / self.nperseg)
        else:
            win = np.ones(self.nperseg)
            
        step = self.nperseg - self.noverlap
        num_segments = (len(signal) - self.nperseg) // step + 1
        
        # Scaling factor U
        U = np.sum(win**2)
        
        spectra = []
        for i in range(num_segments):
            start = i * step
            segment = signal[start:start + self.nperseg].copy()
            
            if self.detrend == "constant":
                segment -= np.mean(segment)
                
            windowed = segment * win
            
            # rfft
            fft_result = np.fft.rfft(windowed)
            
            # periodogram
            if self.scaling == "density":
                Pxx = np.abs(fft_result)**2 / (self.fs * U)
            else: # spectrum
                Pxx = np.abs(fft_result)**2 / U
                
            # one-sided scaling: x2 except DC and Nyquist
            if len(Pxx) > 2:
                if self.nperseg % 2 == 0:
                    Pxx[1:-1] *= 2
                else:
                    Pxx[1:] *= 2
                    
            spectra.append(Pxx)
            
        psd = np.mean(spectra, axis=0)
        freqs = np.fft.rfftfreq(self.nperseg, d=1/self.fs)
        
        return freqs, psd
