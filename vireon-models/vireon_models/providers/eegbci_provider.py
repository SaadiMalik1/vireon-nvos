import os
import mne
from mne.datasets import eegbci
from vireon_core.contracts.dataset_provider import IDatasetProvider
from typing import Tuple, Any, Dict
import numpy as np

class EEGBCIProvider(IDatasetProvider):
    def __init__(self, data_path: str = None):
        self.data_path = data_path or os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'eegbci'))

    def load(self, subject: int, run: int) -> Tuple[Any, np.ndarray, Dict[str, Any]]:
        # Fetch the file if it's not present (eegbci.load_data handles this if we pass path)
        fnames = eegbci.load_data(subject, [run], path=self.data_path)
        raw = mne.io.read_raw_edf(fnames[0], preload=True)
        eegbci.standardize(raw) # Standardize channel names
        
        events, event_id = mne.events_from_annotations(raw)
        
        metadata = {
            "dataset": "PhysioNet EEGBCI",
            "subject": subject,
            "run": run,
            "event_id": event_id,
            "sfreq": raw.info['sfreq'],
            "n_channels": len(raw.ch_names)
        }
        
        return raw, events, metadata
