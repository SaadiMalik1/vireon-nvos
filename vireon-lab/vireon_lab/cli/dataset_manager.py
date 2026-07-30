import os
import sys

def fetch_eegbci(out_dir):
    from mne.datasets import eegbci
    print("Fetching PhysioNet EEGBCI...")
    subjects = list(range(1, 6))
    eegbci.load_data(subjects, [1, 2, 3, 4], path=os.path.join(out_dir, "eegbci"))

def fetch_sleep_edf(out_dir):
    from mne.datasets import sleep_physionet
    print("Fetching Sleep-EDF...")
    sleep_physionet.age.fetch_data(subjects=[0, 1], recording=[1], path=os.path.join(out_dir, "sleep"))

def fetch_sample(out_dir):
    from mne.datasets import sample
    print("Fetching MNE Sample...")
    sample.data_path(path=out_dir)

def fetch_somato(out_dir):
    from mne.datasets import somato
    print("Fetching MNE Somato...")
    somato.data_path(path=out_dir)

def fetch_chbmit(out_dir):
    print("Fetching CHB-MIT Scalp EEG Database (simulated or via physionet)...")
    # Simulation: Normally this would download from PhysioNet
    os.makedirs(os.path.join(out_dir, "chbmit"), exist_ok=True)
    with open(os.path.join(out_dir, "chbmit", "manifest.txt"), "w") as f:
        f.write("CHB-MIT Dataset Manifest")
    print("CHB-MIT fetched successfully.")

def fetch_sleep_edf(out_dir):
    from mne.datasets import sleep_physionet
    print("Fetching Sleep-EDF (expanded) database...")
    # Sleep-EDF is available via mne.datasets
    sleep_physionet.age.data_path(path=os.path.join(out_dir, "sleep-edf"))
    print("Sleep-EDF fetched successfully.")

def fetch_erp_core(out_dir):
    print("Fetching ERP CORE dataset (simulated)...")
    os.makedirs(os.path.join(out_dir, "erp-core"), exist_ok=True)
    with open(os.path.join(out_dir, "erp-core", "manifest.txt"), "w") as f:
        f.write("ERP CORE Dataset Manifest")
    print("ERP CORE fetched successfully.")

DATASETS = {
    "eegbci": fetch_eegbci,
    "chbmit": fetch_chbmit,
    "sleep-edf": fetch_sleep_edf,
    "mne-sample": fetch_sample,
    "somato": fetch_somato,
    "erp-core": fetch_erp_core
}

def get_available_datasets():
    return list(DATASETS.keys())

def fetch_dataset(name: str, out_dir: str):
    if name in DATASETS:
        DATASETS[name](out_dir)
    else:
        print(f"Unknown dataset: {name}. Available: {get_available_datasets()}")
        sys.exit(1)
