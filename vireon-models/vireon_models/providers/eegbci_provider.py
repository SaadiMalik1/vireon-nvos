import os
from typing import Tuple, Any, Dict, Union, List
import mne
from mne.datasets import eegbci
from vireon_core.contracts import IProvider
import numpy as np

class EEGBCIProvider(IProvider):
    def __init__(self, subject_id: int = 1, run_id: Union[int, List[int]] = 1, data_path: str = None):
        self.subject_id = subject_id
        self.run_id = run_id
        self.data_path = data_path or os.path.expanduser("~/mne_data")
        self._data = None

    def start(self) -> None:
        try:
            runs = [self.run_id] if isinstance(self.run_id, int) else list(self.run_id)
            fnames = eegbci.load_data(self.subject_id, runs, path=self.data_path, update_path=True, verbose=False)
            
            raws = [mne.io.read_raw_edf(f, preload=True, verbose=False) for f in fnames]
            if len(raws) == 1:
                raw = raws[0]
            else:
                raw = mne.concatenate_raws(raws, verbose=False)
                
            eegbci.standardize(raw)
            events, event_id = mne.events_from_annotations(raw, verbose=False)
            
            self._data = {
                "dataset": "PhysioNet EEGBCI",
                "subject": self.subject_id,
                "run": self.run_id,
                "event_id": event_id,
                "sample_rate": raw.info['sfreq'],
                "n_channels": len(raw.ch_names),
                "data": raw.get_data().copy(),
                "events": events,
                "raw": raw
            }
        except Exception as e:
            raise FileNotFoundError(f"EEGBCI data not found or failed to load: {e}")

    def stop(self) -> None:
        pass

    def get_data(self) -> Dict[str, Any]:
        if self._data is None:
            self.start()
        return self._data

    def load(self) -> Dict[str, Any]:
        """Convenience method to load epochs / data for pipeline evaluation."""
        data_dict = self.get_data()
        raw = data_dict["raw"]
        events = data_dict["events"]
        event_id = data_dict["event_id"]
        
        # Select motor imagery event codes (T1=left fist, T2=right fist)
        tmin, tmax = 1.0, 3.0
        target_event_id = {k: v for k, v in event_id.items() if k in ['T1', 'T2']}
        if not target_event_id:
            target_event_id = event_id

        epochs = mne.Epochs(
            raw,
            events,
            target_event_id,
            tmin=tmin,
            tmax=tmax,
            proj=True,
            baseline=None,
            preload=True,
            verbose=False
        )
        
        X = epochs.get_data().copy()
        y = epochs.events[:, -1]
        
        return {
            "data": X,
            "label": y,
            "raw_provider_data": data_dict
        }
