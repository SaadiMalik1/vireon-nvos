import os
import mne
from typing import Any

from vireon_core.contracts import IProvider

class MNEProvider(IProvider):
    """
    A provider that wraps MNE-Python to deterministically load and process
    real clinical neurophysiology datasets (EDF, FIF, BDF, etc.).
    """
    def __init__(self, filepath: str, preload: bool = True, filter_l_freq: float = None, filter_h_freq: float = None):
        self.filepath = filepath
        self.preload = preload
        self.filter_l_freq = filter_l_freq
        self.filter_h_freq = filter_h_freq
        self.raw = None
        self.data_dict = {}

    def start(self) -> None:
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"MNEProvider could not find file: {self.filepath}")

        # Deterministically load the data (MNE handles EDF, BDF, FIF seamlessly)
        # We suppress verbose output for cleaner test logs
        mne.set_log_level('WARNING')
        
        # We use read_raw which attempts to infer format, but if it's EDF we can use read_raw_edf
        if self.filepath.lower().endswith('.edf'):
            self.raw = mne.io.read_raw_edf(self.filepath, preload=self.preload, verbose='WARNING')
        elif self.filepath.lower().endswith('.fif'):
            self.raw = mne.io.read_raw_fif(self.filepath, preload=self.preload, verbose='WARNING')
        else:
            # Fallback to generic if supported
            self.raw = mne.io.read_raw(self.filepath, preload=self.preload, verbose='WARNING')

        # Apply deterministic processing if requested
        if self.filter_l_freq is not None or self.filter_h_freq is not None:
            # Ensure data is loaded
            if not self.raw.preload:
                self.raw.load_data()
            self.raw.filter(l_freq=self.filter_l_freq, h_freq=self.filter_h_freq, method='fir', phase='zero-double', verbose='WARNING')

        # Extract data into standard VIREON telemetry dict
        data, times = self.raw[:, :]
        data = data.T  # Transpose to (n_samples, n_channels)
        self.data_dict = {
            "data": data,           # shape: (n_samples, n_channels)
            "times": times,         # shape: (n_samples,)
            "sample_rate": self.raw.info['sfreq'],
            "num_channels": len(self.raw.ch_names),
            "channel_names": self.raw.ch_names,
            "duration_sec": times[-1] if len(times) > 0 else 0.0,
            "seed": 42  # Datasets are fixed; seed is symbolic here unless noise is added later
        }

    def stop(self) -> None:
        if self.raw is not None:
            self.raw.close()
            self.raw = None

    def get_data(self) -> Any:
        return self.data_dict
