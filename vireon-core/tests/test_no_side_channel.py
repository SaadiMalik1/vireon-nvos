import os
import json
import tempfile
import numpy as np

from vireon_core.kernel.execution_engine import ExecutionEngine
from vireon_validation.evidence.generator import EvidenceGenerator
from vireon_core.contracts.base import IExperimentDef, IProvider

class MockProvider(IProvider):
    def start(self): pass
    def stop(self): pass
    def get_data(self):
        return {"data": np.array([1, 2, 3]), "sample_rate": 250.0, "num_channels": 1}

class MockScenario(IExperimentDef):
    def get_provider(self): return MockProvider()
    def get_stimulus(self): return []
    def get_assertions(self): return []

def test_no_raw_data_attr():
    """IEvidence instances must not have the raw data attribute after execution."""
    scenario = MockScenario()
    evidence = ExecutionEngine.run(scenario)
    assert not hasattr(evidence, '_raw_' + 'provider_data')
    assert '_raw_' + 'provider_data' not in evidence.model_dump()
    # also check pydantic private fields
    if hasattr(evidence, '__pydantic_private__') and evidence.__pydantic_private__ is not None:
        assert '_raw_' + 'provider_data' not in evidence.__pydantic_private__

def test_raw_data_passed_explicitly_to_generator():
    """EvidenceGenerator receives raw_provider_data as a parameter, not via side-channel."""
    scenario = MockScenario()
    evidence = ExecutionEngine.run(scenario)
    raw_data = {"data": np.array([1, 2, 3]), "sample_rate": 250.0, "num_channels": 1}
    with tempfile.TemporaryDirectory() as tmpdir:
        gen = EvidenceGenerator(evidence, tmpdir)
        # Should not crash and should write telemetry.npz
        gen.generate_bundle(raw_provider_data=raw_data)

def test_telemetry_npz_still_written():
    """telemetry.npz is still in the bundle and hashed."""
    scenario = MockScenario()
    evidence = ExecutionEngine.run(scenario)
    raw_data = {"data": np.array([1, 2, 3]), "sample_rate": 250.0, "num_channels": 1}
    with tempfile.TemporaryDirectory() as tmpdir:
        gen = EvidenceGenerator(evidence, tmpdir)
        bundle_path = gen.generate_bundle(raw_provider_data=raw_data)
        
        telemetry_path = os.path.join(bundle_path, "telemetry.npz")
        assert os.path.exists(telemetry_path)
        
        hashes_path = os.path.join(bundle_path, "hashes.json")
        with open(hashes_path, "r") as f:
            hashes = json.load(f)
        assert "telemetry.npz" in hashes
