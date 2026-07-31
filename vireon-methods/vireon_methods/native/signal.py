import numpy as np
from scipy import signal

class VireonButterworth:
    """
    Native VIREON implementation of Butterworth filtering.
    """
    plugin_id = "vireon.methods.signal.butterworth"
    version = "1.0.0"
    
    def __init__(self, order: int, cutoff: float, fs: float, btype: str = 'low'):
        self.order = order
        self.cutoff = cutoff
        self.fs = fs
        self.btype = btype
        self.b, self.a = signal.butter(order, cutoff, btype=btype, fs=fs)
        
    def process(self, data: np.ndarray) -> np.ndarray:
        return signal.filtfilt(self.b, self.a, data, axis=-1)

class VireonNotch:
    """
    Native VIREON implementation of Notch filtering.
    """
    plugin_id = "vireon.methods.signal.notch"
    version = "1.0.0"
    
    def __init__(self, freq: float, q: float, fs: float):
        self.freq = freq
        self.q = q
        self.fs = fs
        self.b, self.a = signal.iirnotch(freq, q, fs)
        
    def process(self, data: np.ndarray) -> np.ndarray:
        return signal.filtfilt(self.b, self.a, data, axis=-1)

class VireonResample:
    """
    Native VIREON implementation of signal resampling.
    """
    plugin_id = "vireon.methods.signal.resample"
    version = "1.0.0"
    
    def __init__(self, up: int, down: int):
        self.up = up
        self.down = down
        
    def process(self, data: np.ndarray) -> np.ndarray:
        return signal.resample_poly(data, self.up, self.down, axis=-1)

class VireonBaselineCorrection:
    """
    Native VIREON implementation of baseline correction.
    """
    plugin_id = "vireon.methods.signal.baseline"
    version = "1.0.0"
    
    def __init__(self, baseline_window: tuple):
        self.baseline_window = baseline_window
        
    def process(self, data: np.ndarray) -> np.ndarray:
        # Subtract mean of the baseline window (assuming data is epochs x channels x time)
        start, end = self.baseline_window
        baseline_mean = np.mean(data[..., start:end], axis=-1, keepdims=True)
        return data - baseline_mean
