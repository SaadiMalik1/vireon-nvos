"""DEPRECATED: This native implementation is retained for reference only.
VIREON now delegates to mature libraries (MOABB, MNE, scipy, sklearn, pyriemann).
Use the corresponding adapter in vireon_moabb.adapters instead.

This file will be removed in v2.1.0.
"""
import numpy as np
import scipy.signal.windows
from typing import Tuple
from vireon_core.contracts.plugin import ScientificContractViolation

class VireonMultitaper:
    """Multitaper Power Spectral Density (PSD) estimator using Slepian (DPSS) tapers.
    
    Reference: Thomson, D. J. (1982). Spectrum estimation and harmonic analysis. 
    Proceedings of the IEEE, 70(9), 1055-1096. DOI: 10.1109/PROC.1982.12433
    """
    
    def __init__(self, fs: float, NW: float = 2.5, n_tapers: int = None):
        self.fs = fs
        self.NW = NW
        self.n_tapers = n_tapers if n_tapers is not None else int(2 * NW - 1)
        
    def compute(self, signal: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Compute multitaper spectral estimate.
        
        Args:
            signal: 1D input array.
            
        Returns:
            (freqs, psd)
        """
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
        if N < 4:
            raise ScientificContractViolation(
                "Signal too short for multitaper analysis.",
                violated_assumption="sufficient_length",
                details=f"Signal length {N} < 4.",
                remediation="Provide longer signal."
            )
            
        # Generate DPSS tapers
        dpss = scipy.signal.windows.dpss(N, NW=self.NW, Kmax=self.n_tapers)
        
        # Mean center signal
        sig_centered = signal - np.mean(signal)
        
        # Tapered spectra
        tapered_spectra = []
        for taper in dpss:
            tapered_sig = sig_centered * taper
            fft_res = np.fft.rfft(tapered_sig)
            # Power spectral density scaling
            Pxx = (np.abs(fft_res) ** 2) / self.fs
            if len(Pxx) > 2:
                if N % 2 == 0:
                    Pxx[1:-1] *= 2
                else:
                    Pxx[1:] *= 2
            tapered_spectra.append(Pxx)
            
        psd = np.mean(tapered_spectra, axis=0)
        freqs = np.fft.rfftfreq(N, d=1.0 / self.fs)
        
        return freqs, psd
