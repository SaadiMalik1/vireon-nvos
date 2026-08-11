"""DEPRECATED: This native implementation is retained for reference only.
VIREON now delegates to mature libraries (MOABB, MNE, scipy, sklearn, pyriemann).
Use the corresponding adapter in vireon_moabb.adapters instead.

This file will be removed in v2.1.0.
"""
import numpy as np
import scipy.interpolate
from typing import List, Tuple
from vireon_core.contracts.plugin import ScientificContractViolation

class VireonEMD:
    """Empirical Mode Decomposition (EMD) algorithm.
    
    Reference: Huang, N. E., et al. (1998). The empirical mode decomposition and 
    the Hilbert spectrum for nonlinear and non-stationary time series analysis. 
    Proceedings of the Royal Society A, 454(1971), 903-995. DOI: 10.1098/rspa.1998.0193
    """
    
    def __init__(self, max_imfs: int = 5, max_sift_iterations: int = 100, sd_threshold: float = 0.2):
        self.max_imfs = max_imfs
        self.max_sift_iterations = max_sift_iterations
        self.sd_threshold = sd_threshold
        
    def _find_extrema(self, signal: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Identify indices of local maxima and local minima."""
        d = np.diff(signal)
        maxima = np.where((d[:-1] > 0) & (d[1:] < 0))[0] + 1
        minima = np.where((d[:-1] < 0) & (d[1:] > 0))[0] + 1
        return maxima, minima
        
    def fit_transform(self, signal: np.ndarray) -> List[np.ndarray]:
        """Extract Intrinsic Mode Functions (IMFs).
        
        Args:
            signal: 1D input array.
            
        Returns:
            List of IMFs (each same length as signal) plus final residue.
        """
        if not isinstance(signal, np.ndarray):
            signal = np.array(signal, dtype=float)
            
        if np.any(np.isnan(signal)) or np.any(np.isinf(signal)):
            raise ScientificContractViolation(
                "Signal contains NaN or Inf values.",
                violated_assumption="finite_values",
                details="NaN or Inf detected.",
                remediation="Clean data."
            )
            
        N = len(signal)
        if N < 6:
            raise ScientificContractViolation(
                "Signal too short for EMD decomposition.",
                violated_assumption="sufficient_length",
                details=f"Signal length {N} < 6.",
                remediation="Provide longer signal."
            )
            
        imfs = []
        residue = signal.copy()
        t = np.arange(N)
        
        for k in range(self.max_imfs):
            h = residue.copy()
            for it in range(self.max_sift_iterations):
                maxima, minima = self._find_extrema(h)
                if len(maxima) < 2 or len(minima) < 2:
                    break
                    
                # Boundary conditions: extend endpoints
                max_t = np.r_[0, maxima, N - 1]
                max_val = np.r_[h[0], h[maxima], h[-1]]
                min_t = np.r_[0, minima, N - 1]
                min_val = np.r_[h[0], h[minima], h[-1]]
                
                # Cubic spline envelopes
                env_max = scipy.interpolate.CubicSpline(max_t, max_val, bc_type='natural')(t)
                env_min = scipy.interpolate.CubicSpline(min_t, min_val, bc_type='natural')(t)
                
                mean_env = (env_max + env_min) / 2.0
                h_prev = h.copy()
                h = h - mean_env
                
                # Stopping criterion (standard deviation of sifting)
                sd = np.sum((h_prev - h) ** 2) / (np.sum(h_prev ** 2) + 1e-12)
                if sd < self.sd_threshold:
                    break
                    
            imfs.append(h)
            residue -= h
            
            # Check if residue is monotonic
            maxima_r, minima_r = self._find_extrema(residue)
            if len(maxima_r) < 2 or len(minima_r) < 2:
                break
                
        imfs.append(residue)
        return imfs
