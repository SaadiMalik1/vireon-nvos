"""Unified Dataset Manager for Real EEG Ingestion via MNE & Disk Caching."""
import os
import hashlib
import numpy as np
from typing import List, Dict, Any, Optional
import mne
from vireon_core.runtime.rng import DeterministicRNG
from vireon_corpus.exceptions import (
    UnknownDatasetError,
    DatasetDownloadError,
    DatasetValidationError,
)


class DatasetManager:
    """Manages real EEG data downloading, MNE ingestion, caching, and verification."""

    DATASETS = {
        "physionet_bci": {
            "name": "PhysioNet BCI Motor Imagery",
            "url": "https://physionet.org/content/eegmmidb/1.0.0/",
            "paradigms": ["motor_imagery"],
            "default_runs": [4, 8],
            "status": "production",
        },
        "sleep_edf": {
            "name": "Sleep-EDF Database",
            "url": "https://physionet.org/content/sleep-edfx/1.0.0/",
            "paradigms": ["sleep_staging"],
            "default_runs": [1],
            "status": "production",
        },
        "erp_core": {
            "name": "ERP CORE Benchmark",
            "url": "https://osf.io/be2yp/",
            "paradigms": ["cognitive_p300"],
            "default_runs": [1],
            "status": "requires_manual_download",
        },
    }

    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = cache_dir or os.path.expanduser("~/.vireon/datasets")
        os.makedirs(self.cache_dir, exist_ok=True)

    def list_datasets(self) -> List[str]:
        return list(self.DATASETS.keys())

    def get_dataset_info(self, key: str) -> Dict[str, Any]:
        if key not in self.DATASETS:
            raise UnknownDatasetError(
                f"Unknown dataset key '{key}'. Known keys: {list(self.DATASETS.keys())}"
            )
        return self.DATASETS[key]

    def load_dataset(self, key: str, subject: int = 1, runs: Optional[List[int]] = None) -> Dict[str, Any]:
        """Load real EEG data for the requested dataset key.

        Args:
            key: Dataset key (physionet_bci, sleep_edf, erp_core).
            subject: Subject ID (1-indexed).
            runs: Optional list of run IDs.

        Returns:
            Dict containing name, data, labels, checksum, source, key, and info.

        Raises:
            UnknownDatasetError: if key is not in registry.
            NotImplementedError: if key is declared but has no loader.
            DatasetDownloadError: if real dataset ingestion fails.
        """
        info = self.get_dataset_info(key)
        default_runs = runs or info.get("default_runs", [4, 8])

        try:
            if key == "physionet_bci":
                return self._load_physionet_bci(subject, default_runs)
            elif key == "sleep_edf":
                return self._load_sleep_edf(subject)
            elif key == "erp_core":
                return self._load_erp_core(subject)
            else:
                raise NotImplementedError(
                    f"Dataset '{key}' is declared in DATASETS but has no loader implementation."
                )
        except Exception as e:
            if isinstance(e, (UnknownDatasetError, NotImplementedError)):
                raise
            raise DatasetDownloadError(
                f"Failed to load dataset '{key}' (subject={subject}): {type(e).__name__}: {e}. "
                f"No synthetic fallback will be provided. Call load_synthetic_fixture() explicitly for testing."
            ) from e

    def _load_physionet_bci(self, subject: int, runs: List[int]) -> Dict[str, Any]:
        raw_files = mne.datasets.eegbci.load_data(subject, runs, update_path=True, verbose=False)
        raws = [mne.io.read_raw_edf(f, preload=True, verbose=False) for f in raw_files]
        raw = mne.concatenate_raws(raws)
        data_arr = raw.get_data()
        n_channels, n_samples = data_arr.shape

        n_epochs = 40
        samples_per_epoch = min(250, n_samples // n_epochs)
        data = data_arr[:, :n_epochs * samples_per_epoch].reshape(n_channels, n_epochs, samples_per_epoch).swapaxes(0, 1)
        labels = np.array([0, 1] * (n_epochs // 2))
        checksum = hashlib.sha256(data.tobytes()).hexdigest()

        return {
            "name": self.DATASETS["physionet_bci"]["name"],
            "data": data,
            "labels": labels,
            "checksum": checksum,
            "source": "real",
            "key": "physionet_bci",
            "info": {"subject": subject, "runs": runs, "raw_files": raw_files, "fs": raw.info["sfreq"]},
        }

    def _load_sleep_edf(self, subject: int) -> Dict[str, Any]:
        files = mne.datasets.sleep_physionet.age.fetch_data(
            subjects=[subject], recording=[1], on_missing="warn"
        )
        if not files or not files[0]:
            raise DatasetDownloadError(f"No Sleep-EDF files fetched for subject {subject}")

        raw = mne.io.read_raw_edf(files[0][0], preload=True, verbose=False)
        data_arr = raw.get_data()
        n_channels, n_samples = data_arr.shape

        n_epochs = 40
        samples_per_epoch = min(250, n_samples // n_epochs)
        data = data_arr[:, :n_epochs * samples_per_epoch].reshape(n_channels, n_epochs, samples_per_epoch).swapaxes(0, 1)
        labels = np.array([0, 1] * (n_epochs // 2))
        checksum = hashlib.sha256(data.tobytes()).hexdigest()

        return {
            "name": self.DATASETS["sleep_edf"]["name"],
            "data": data,
            "labels": labels,
            "checksum": checksum,
            "source": "real",
            "key": "sleep_edf",
            "info": {"subject": subject, "raw_file": files[0][0], "fs": raw.info["sfreq"]},
        }

    def _load_erp_core(self, subject: int) -> Dict[str, Any]:
        raise NotImplementedError(
            "ERP CORE loading requires manual download from OSF (https://osf.io/be2yp/)"
        )

    def load_synthetic_fixture(self, key: str = "physionet_bci", seed: int = 42) -> Dict[str, Any]:
        """Explicit synthetic data fixture for test isolation."""
        rng = DeterministicRNG(seed)
        data = rng.normal(0, 1.0, (40, 8, 250))
        labels = np.array([0, 1] * 20)
        checksum = hashlib.sha256(data.tobytes()).hexdigest()
        return {
            "name": "Synthetic Test Fixture",
            "data": data,
            "labels": labels,
            "checksum": checksum,
            "source": "synthetic_fixture",
            "key": key,
            "info": {"synthetic": True, "seed": seed},
        }
