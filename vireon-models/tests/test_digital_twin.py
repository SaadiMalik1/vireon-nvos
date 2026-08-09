import numpy as np
from vireon_models.patient import DigitalPatient, BrainNetwork
from vireon_models.forward import RandomMixingMatrix

def test_brain_network_generation():
    network = BrainNetwork(num_nodes=4, seed=42)
    sources = network.generate_source_activity(num_samples=250, sample_rate=250.0)
    
    assert sources.shape == (250, 4)
    # Check that it isn't completely flat
    assert np.std(sources) > 0.1

def test_leadfield_projection():
    from vireon_core.runtime.rng import DeterministicRNG
    rng = DeterministicRNG(seed=42)
    sources = rng.normal(0, 1, (250, 4)).astype(np.float32)
    projector = RandomMixingMatrix(num_sources=4, num_sensors=8, seed=42)
    sensors = projector.project(sources)
    
    # 4 sources mapped to 8 sensors
    assert sensors.shape == (250, 8)
    
def test_digital_patient():
    patient = DigitalPatient(age=30, seed=42)
    sources = patient.generate_brain_activity(duration_sec=1.0, sample_rate=250.0)
    assert sources.shape == (250, 4)
