import pytest
from vireon_corpus.dataset_manager import DatasetManager
from vireon_corpus.exceptions import (
    UnknownDatasetError,
)


def test_dataset_manager_list_and_info():
    dm = DatasetManager()
    datasets = dm.list_datasets()
    assert "physionet_bci" in datasets
    assert "sleep_edf" in datasets

    info = dm.get_dataset_info("physionet_bci")
    assert info["name"] == "PhysioNet BCI Motor Imagery"

    with pytest.raises(UnknownDatasetError):
        dm.get_dataset_info("unknown_key")


def test_dataset_manager_synthetic_fixture():
    dm = DatasetManager()
    fixture = dm.load_synthetic_fixture(key="physionet_bci", seed=42)
    assert fixture["source"] == "synthetic_fixture"
    assert fixture["data"].shape == (40, 8, 250)
    assert len(fixture["checksum"]) == 64
