import pytest
from vireon_lab.experiments.base import _build_provider
import os

def test_build_eegbci_provider_not_found():
    config = {
        "provider": "eegbci",
        "config": {
            "subject_id": 999,
            "run_id": 999,
            "data_path": "/tmp/nonexistent_path_eegbci"
        }
    }
    
    provider = _build_provider(config)
    with pytest.raises(FileNotFoundError, match="EEGBCI data not found"):
        provider.start()
