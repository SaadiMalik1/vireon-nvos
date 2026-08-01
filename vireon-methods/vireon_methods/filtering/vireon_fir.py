import numpy as np
from typing import Union, Tuple
from scipy.signal import filtfilt
from vireon_core.contracts.plugin import ScientificContractViolation

class VireonFIR:
    """FIR filter via windowed-sinc design.
    
    Reference: Ifeachor & Jervis, Digital Signal Processing: A Practical Approach.
    """
    
    def __init__(self, fs: float, cutoff: Union[float, Tuple[float, float], list, np.ndarray],
                 numtaps: int = 101, window: str = "hamming",
                 pass_zero: bool = True):
        self.fs = fs
        if isinstance(cutoff, (list, tuple, np.ndarray)):
            self.cutoff = tuple(cutoff)
        else:
            self.cutoff = float(cutoff)
        self.numtaps = numtaps
        self.window = window
        self.pass_zero = pass_zero
        
        if numtaps % 2 == 0:
            # SciPy firwin allows even numtaps for some filters, but we require odd for Type I
            if (isinstance(self.cutoff, tuple) and pass_zero) or (not isinstance(self.cutoff, tuple) and not pass_zero):
                # Highpass or Bandstop with even numtaps is Type II, which has zero at Nyquist -> impossible
                raise ValueError("A filter with an even number of coefficients must have zero response at the Nyquist frequency.")
                
        self.coeffs = self.design()
        
    def design(self) -> np.ndarray:
        """Returns filter coefficients (numtaps,)."""
        N = self.numtaps
        M = N - 1
        n = np.arange(N)
        alpha = M / 2.0
        m = n - alpha
        
        # 1. Compute ideal sinc filter
        if not isinstance(self.cutoff, tuple):
            fc = self.cutoff / self.fs
            if self.pass_zero:
                # Lowpass
                h = 2 * fc * np.sinc(2 * fc * m)
            else:
                # Highpass
                h = -2 * fc * np.sinc(2 * fc * m)
                if alpha.is_integer():
                    h[int(alpha)] += 1.0
        else:
            fc1 = self.cutoff[0] / self.fs
            fc2 = self.cutoff[1] / self.fs
            if not self.pass_zero:
                # Bandpass
                h = 2 * fc2 * np.sinc(2 * fc2 * m) - 2 * fc1 * np.sinc(2 * fc1 * m)
            else:
                # Bandstop
                h = 2 * fc1 * np.sinc(2 * fc1 * m) - 2 * fc2 * np.sinc(2 * fc2 * m)
                if alpha.is_integer():
                    h[int(alpha)] += 1.0
                    
        # 2. Apply window
        if self.window == "hamming":
            w = 0.54 - 0.46 * np.cos(2 * np.pi * n / M)
        elif self.window == "hann":
            w = 0.5 - 0.5 * np.cos(2 * np.pi * n / M)
        elif self.window == "blackman":
            w = 0.42 - 0.5 * np.cos(2 * np.pi * n / M) + 0.08 * np.cos(4 * np.pi * n / M)
        elif self.window == "kaiser":
            raise NotImplementedError("Kaiser window requires beta parameter.")
        else:
            # default rect
            w = np.ones(N)
            
        coeffs = h * w
        
        # 3. Normalize
        if not isinstance(self.cutoff, tuple):
            if self.pass_zero:
                # Lowpass: normalize at DC
                coeffs /= np.sum(coeffs)
            else:
                # Highpass: normalize at Nyquist
                resp = np.sum(coeffs * ((-1)**n))
                coeffs /= np.abs(resp)
        else:
            if not self.pass_zero:
                # Bandpass: normalize at center frequency
                center_freq = (fc1 + fc2) / 2.0
                resp = np.sum(coeffs * np.exp(-1j * 2 * np.pi * center_freq * n))
                coeffs /= np.abs(resp)
            else:
                # Bandstop: normalize at DC
                coeffs /= np.sum(coeffs)
                
        return coeffs
        
    def apply(self, data: np.ndarray) -> np.ndarray:
        """Zero-phase filter via scipy.signal.filtfilt."""
        if not isinstance(data, np.ndarray):
            data = np.array(data)
            
        if np.any(np.isnan(data)) or np.any(np.isinf(data)):
            raise ScientificContractViolation(
                "Signal contains NaN or Inf values.",
                violated_assumption="finite_values",
                details="NaN or Inf detected.",
                remediation="Clean data."
            )
            
        return filtfilt(self.coeffs, [1.0], data, axis=-1)
