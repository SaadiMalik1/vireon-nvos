import pytest
from vireon_core.contracts.base import IExperiment, SignalType, IExperimentDef, IProvider, IStimulus, IAssertion
from vireon_core.contracts.device import ReferenceDevice

class DummyProvider(IProvider):
    def start(self): pass
    def stop(self): pass
    def get_data(self): return "data"

class DummyScenario(IExperimentDef):
    def get_provider(self):
        return DummyProvider()
    def get_stimulus(self):
        return []
    def get_assertions(self):
        return []

def test_experiment_creation():
    scenario = DummyScenario()
    device = ReferenceDevice(name="DummyADC", specs={"channels": 8})
    
    experiment = IExperiment(
        hypothesis="Signal processing correctly identifies artifacts",
        signal_type=SignalType.EEG,
        experiment_def=scenario
    )
    
    assert experiment.hypothesis == "Signal processing correctly identifies artifacts"
    assert experiment.signal_type == SignalType.EEG
