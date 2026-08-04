import numpy as np
from typing import Union
from vireon_core.contracts.plugin import ScientificContractViolation

class VireonConvolution:
    """1D Convolution and Cross-Correlation module.
    
    Reference: Oppenheim, A. V., & Schafer, R. W. (2009). Discrete-Time Signal Processing. 
    Pearson Higher Education.
    """
    
    def __init__(self, mode: str = "full", method: str = "auto"):
        if mode not in ["full", "same", "valid"]:
            raise ValueError(f"Invalid mode {mode}. Expected 'full', 'same', or 'valid'.")
        self.mode = mode
        self.method = method
        
    def convolve(self, in1: np.ndarray, in2: np.ndarray) -> np.ndarray:
        """Linear convolution of 1D signals in1 and in2."""
        in1 = np.asarray(in1, dtype=float)
        in2 = np.asarray(in2, dtype=float)
        
        if np.any(np.isnan(in1)) or np.any(np.isinf(in1)) or np.any(np.isnan(in2)) or np.any(np.isinf(in2)):
            raise ScientificContractViolation(
                "Input contains NaN or Inf values.",
                violated_assumption="finite_values",
                details="NaN or Inf detected.",
                remediation="Clean data."
            )
            
        return np.convolve(in1, in2, mode=self.mode)
        
    def correlate(self, in1: np.ndarray, in2: np.ndarray) -> np.ndarray:
        """Cross-correlation of 1D signals in1 and in2."""
        in1 = np.asarray(in1, dtype=float)
        in2 = np.asarray(in2, dtype=float)
        
        if np.any(np.isnan(in1)) or np.any(np.isinf(in1)) or np.any(np.isnan(in2)) or np.any(np.isinf(in2)):
            raise ScientificContractViolation(
                "Input contains NaN or Inf values.",
                violated_assumption="finite_values",
                details="NaN or Inf detected.",
                remediation="Clean data."
            )
            
        return np.correlate(in1, in2, mode=self.mode)
