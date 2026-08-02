from vireon_core.runtime.rng import DeterministicRNG
import mne
from mne_bids import BIDSPath, write_raw_bids
import os
import numpy as np

def convert_to_bids_mock(bids_dir, name):
    bids_out = os.path.join(bids_dir, name)
    
    info = mne.create_info(ch_names=['Fp1', 'Fp2', 'Cz'], sfreq=100.0, ch_types='eeg')
    info.set_montage('standard_1020')
    rng = DeterministicRNG(seed=42)
    data = rng.normal(0, 1, (3, 1000))
    raw = mne.io.RawArray(data, info)
    
    events = np.array([[100, 0, 1], [300, 0, 2]])
    event_id = {'CondA': 1, 'CondB': 2}
    
    bids_path = BIDSPath(subject='01', task='task', root=bids_out, datatype='eeg')
    
    write_raw_bids(raw, bids_path, events=events, event_id=event_id, overwrite=True, format='EDF', allow_preload=True)

import tempfile
d = tempfile.mkdtemp()
convert_to_bids_mock(d, 'test_dataset')
print(os.listdir(os.path.join(d, 'test_dataset')))
