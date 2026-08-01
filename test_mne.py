import mne
raw_fnames = mne.datasets.eegbci.load_data(1, [4, 8, 12])
print("Downloaded files:", raw_fnames)
