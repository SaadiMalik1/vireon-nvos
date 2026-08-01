import mne
raw = mne.io.read_raw_edf('/home/ronin/mne_data/MNE-eegbci-data/files/eegmmidb/1.0.0/S001/S001R04.edf', preload=True)
events, event_id = mne.events_from_annotations(raw)
print(raw.info)
print(events.shape)
