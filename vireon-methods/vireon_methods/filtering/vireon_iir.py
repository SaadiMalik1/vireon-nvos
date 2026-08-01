import numpy as np
from typing import Union, Tuple
from scipy.signal import filtfilt, lfilter
from vireon_core.contracts.plugin import ScientificContractViolation

class VireonIIR:
    """IIR filter (Butterworth) via bilinear transform.
    
    Reference: Oppenheim & Schafer, Discrete-Time Signal Processing.
    """
    def __init__(self, fs: float, cutoff: Union[float, Tuple[float, float], list, np.ndarray],
                 btype: str = "lowpass", order: int = 4,
                 filter_type: str = "butter", rp: float = 5, rs: float = 40):
        self.fs = fs
        if isinstance(cutoff, (list, tuple, np.ndarray)):
            self.cutoff = tuple(cutoff)
        else:
            self.cutoff = float(cutoff)
            
        self.btype = btype.lower()
        if self.btype not in ["lowpass", "highpass", "bandpass", "bandstop"]:
            if self.btype == "low": self.btype = "lowpass"
            elif self.btype == "high": self.btype = "highpass"
            elif self.btype == "band": self.btype = "bandpass"
            elif self.btype == "stop": self.btype = "bandstop"
            else:
                raise ValueError("btype must be lowpass, highpass, bandpass, or bandstop")
                
        self.order = order
        self.filter_type = filter_type.lower()
        
        if self.filter_type != "butter":
            raise NotImplementedError("Only 'butter' filter type is currently supported.")
            
        self.rp = rp
        self.rs = rs
        self.b, self.a = self.design()
        
    def design(self) -> Tuple[np.ndarray, np.ndarray]:
        """Returns (b, a) coefficients."""
        N = self.order
        fs = self.fs
        
        # Analog prototype for Butterworth
        n = np.arange(1, N + 1)
        p = np.exp(1j * (np.pi * (2 * n - 1) / (2 * N) + np.pi / 2))
        k = 1.0
        
        if self.btype in ["lowpass", "highpass"]:
            if isinstance(self.cutoff, tuple):
                raise ValueError("cutoff must be a scalar for lowpass or highpass filters")
            fc = self.cutoff
            wd = np.pi * (fc / (fs / 2))
            wa = 2 * fs * np.tan(wd / 2)
            
            if self.btype == "lowpass":
                p_a = p * wa
                z_a = np.array([])
                k_a = k * wa**N
                
                p_d = (2 * fs + p_a) / (2 * fs - p_a)
                z_d = -np.ones(N)
                k_d = k_a / np.prod(2 * fs - p_a)
                
            else: # highpass
                p_a = wa / p
                z_a = np.zeros(N)
                k_a = k / np.prod(-p)
                
                p_d = (2 * fs + p_a) / (2 * fs - p_a)
                z_d = np.ones(N)
                k_d = k_a * (2 * fs)**N / np.prod(2 * fs - p_a)
                
        else: # bandpass or bandstop
            if not isinstance(self.cutoff, tuple) or len(self.cutoff) != 2:
                raise ValueError("cutoff must be a tuple of (f1, f2) for band filters")
            
            w1 = 2 * fs * np.tan(np.pi * self.cutoff[0] / fs)
            w2 = 2 * fs * np.tan(np.pi * self.cutoff[1] / fs)
            w0 = np.sqrt(w1 * w2)
            bw = w2 - w1
            
            if self.btype == "bandpass":
                p_a = []
                for p_k in p:
                    val = np.sqrt(bw**2 * p_k**2 - 4 * w0**2 + 0j)
                    p_a.append((bw * p_k + val) / 2)
                    p_a.append((bw * p_k - val) / 2)
                p_a = np.array(p_a)
                
                z_a = np.zeros(N)
                k_a = bw**N
                
                p_d = (2 * fs + p_a) / (2 * fs - p_a)
                z_d = np.concatenate([np.ones(N), -np.ones(N)])
                k_d = k_a * (2 * fs)**N / np.prod(2 * fs - p_a)
                
            else: # bandstop
                p_a = []
                for p_k in p:
                    val = np.sqrt((bw / p_k)**2 - 4 * w0**2 + 0j)
                    p_a.append((bw / p_k + val) / 2)
                    p_a.append((bw / p_k - val) / 2)
                p_a = np.array(p_a)
                
                z_a = np.concatenate([1j * w0 * np.ones(N), -1j * w0 * np.ones(N)])
                k_a = 1.0
                
                p_d = (2 * fs + p_a) / (2 * fs - p_a)
                z_d = (2 * fs + z_a) / (2 * fs - z_a)
                k_d = k_a * np.prod(2 * fs - z_a) / np.prod(2 * fs - p_a)
                
        b = np.real(k_d * np.poly(z_d))
        a = np.real(np.poly(p_d))
        
        return b, a

    def apply(self, data: np.ndarray, zero_phase: bool = True) -> np.ndarray:
        if not isinstance(data, np.ndarray):
            data = np.array(data)
            
        if np.any(np.isnan(data)) or np.any(np.isinf(data)):
            raise ScientificContractViolation(
                "Signal contains NaN or Inf values.",
                violated_assumption="finite_values",
                details="NaN or Inf detected.",
                remediation="Clean data."
            )
            
        if zero_phase:
            return filtfilt(self.b, self.a, data, axis=-1)
        else:
            return lfilter(self.b, self.a, data, axis=-1)
