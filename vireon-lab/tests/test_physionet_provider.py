import pytest
from vireon_lab.experiments.base import _build_provider

def test_build_physionet_provider_not_found():
    config = {
        "provider": "physionet_mi",
        "config": {
            "subject_id": 999,
            "run_id": 999
        }
    }
    
    with pytest.raises(FileNotFoundError, match="PhysioNet data not found"):
        provider = _build_provider(config)
