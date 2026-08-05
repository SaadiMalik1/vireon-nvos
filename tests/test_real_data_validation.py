"""Real-Data Algorithm Benchmarks Suite."""
import pytest
import numpy as np
from vireon_corpus.dataset_manager import DatasetManager
from vireon_methods.spatial.vireon_csp import VireonCSP
from vireon_methods.spectral.vireon_welch import VireonWelch
from vireon_methods.connectivity.vireon_connectivity import VireonWPLI


@pytest.fixture
def dataset_mgr():
    return DatasetManager()


def test_real_data_physionet_csp(dataset_mgr):
    ds = dataset_mgr.load_dataset("physionet_bci")
    csp = VireonCSP(n_components=4)
    feats = csp.fit_transform(ds["data"], ds["labels"])
    assert feats.shape == (40, 4)


def test_real_data_sleep_edf_welch(dataset_mgr):
    ds = dataset_mgr.load_dataset("sleep_edf")
    welch = VireonWelch(fs=100.0, nperseg=200)
    f, psd = welch.compute(ds["data"][0, 0])
    assert len(f) == len(psd)
    assert len(f) > 0


def test_real_data_chb_mit_wpli(dataset_mgr):
    ds = dataset_mgr.load_dataset("chb_mit")
    wpli = VireonWPLI().compute(ds["data"][0, :2], fs=256.0, band=(8, 12))
    assert isinstance(wpli, float) or isinstance(wpli, np.ndarray)


def test_real_data_erp_core_checksum(dataset_mgr):
    ds = dataset_mgr.load_dataset("erp_core")
    assert len(ds["checksum"]) == 64


def test_real_data_bci_comp_iv_2a_loading(dataset_mgr):
    ds = dataset_mgr.load_dataset("bci_comp_iv_2a")
    assert ds["data"].shape[0] == 40
