import numpy as np
from vireon_core.contracts.plugin import ScientificContractViolation

class VireonConvolution:
    """1D FFT-based Convolution (Overlap-Add / Fast FFT) and Cross-Correlation module.
    
    Reference: Oppenheim, A. V., & Schafer, R. W. (2009). Discrete-Time Signal Processing. 
    Pearson Higher Education.
    """
    
    def __init__(self, mode: str = "full", method: str = "fft"):
        if mode not in ["full", "same", "valid"]:
            raise ValueError(f"Invalid mode {mode}. Expected 'full', 'same', or 'valid'.")
        self.mode = mode
        self.method = method
        
    def convolve(self, in1: np.ndarray, in2: np.ndarray) -> np.ndarray:
        """Linear FFT-based convolution (overlap_add fast convolution) of 1D signals in1 and in2."""
        in1 = np.asarray(in1, dtype=float)
        in2 = np.asarray(in2, dtype=float)
        
        if np.any(np.isnan(in1)) or np.any(np.isinf(in1)) or np.any(np.isnan(in2)) or np.any(np.isinf(in2)):
            raise ScientificContractViolation(
                "Input contains NaN or Inf values.",
                violated_assumption="finite_values",
                details="NaN or Inf detected.",
                remediation="Clean data."
            )
            
        n1, n2 = len(in1), len(in2)
        n_fft = n1 + n2 - 1
        # Fast FFT length (next power of 2 for overlap_add / fast rfft/irfft)
        n_fft_pad = 1 << (n_fft - 1).bit_length()
        X = np.fft.rfft(in1, n_fft_pad)
        H = np.fft.rfft(in2, n_fft_pad)
        y = np.fft.irfft(X * H, n_fft_pad)[:n_fft]
        
        if self.mode == "full":
            return y
        elif self.mode == "same":
            start = (n2 - 1) // 2
            return y[start:start + n1]
        elif self.mode == "valid":
            if n1 >= n2:
                return y[n2 - 1:n1]
            else:
                return y[n1 - 1:n2]
        return y
        
    def correlate(self, in1: np.ndarray, in2: np.ndarray) -> np.ndarray:
        """FFT-based cross-correlation of 1D signals in1 and in2."""
        in1 = np.asarray(in1, dtype=float)
        in2 = np.asarray(in2, dtype=float)
        
        if np.any(np.isnan(in1)) or np.any(np.isinf(in1)) or np.any(np.isnan(in2)) or np.any(np.isinf(in2)):
            raise ScientificContractViolation(
                "Input contains NaN or Inf values.",
                violated_assumption="finite_values",
                details="NaN or Inf detected.",
                remediation="Clean data."
            )
            
        n1, n2 = len(in1), len(in2)
        n_fft = n1 + n2 - 1
        n_fft_pad = 1 << (n_fft - 1).bit_length()
        X = np.fft.rfft(in1, n_fft_pad)
        H = np.fft.rfft(in2[::-1], n_fft_pad)
        y = np.fft.irfft(X * H, n_fft_pad)[:n_fft]
        
        if self.mode == "full":
            return y
        elif self.mode == "same":
            start = (n2 - 1) // 2
            return y[start:start + n1]
        elif self.mode == "valid":
            if n1 >= n2:
                return y[n2 - 1:n1]
            else:
                return y[n1 - 1:n2]
        return y
