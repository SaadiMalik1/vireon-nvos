import os
import mne
from mne.datasets import eegbci
from vireon_core.contracts import IProvider
from typing import Tuple, Any, Dict
import numpy as np

class EEGBCIProvider(IProvider):
    def __init__(self, subject_id: int = 1, run_id: int = 1, data_path: str = None):
        self.subject_id = subject_id
        self.run_id = run_id
        self.data_path = data_path or os.path.expanduser("~/mne_data")
        self._data = None

    def start(self) -> None:
        try:
            fnames = eegbci.load_data(self.subject_id, [self.run_id], path=self.data_path)
            raw = mne.io.read_raw_edf(fnames[0], preload=True, verbose=False)
            eegbci.standardize(raw)
            events, event_id = mne.events_from_annotations(raw, verbose=False)
            
            self._data = {
                "dataset": "PhysioNet EEGBCI",
                "subject": self.subject_id,
                "run": self.run_id,
                "event_id": event_id,
                "sample_rate": raw.info['sfreq'],
                "n_channels": len(raw.ch_names),
                "data": raw.get_data(copy=True),
                "events": events
            }
        except Exception as e:
            raise FileNotFoundError(f"EEGBCI data not found or failed to load: {e}")

    def stop(self) -> None:
        pass

    def get_data(self) -> Dict[str, Any]:
        if self._data is None:
            self.start()
        return self._data
