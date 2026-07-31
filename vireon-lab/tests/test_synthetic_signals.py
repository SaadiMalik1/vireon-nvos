import pytest
import numpy as np
from vireon_lab.synthetic.generators import OscillationGenerator, CognitiveGenerator, ClinicalGenerator, ArtifactGenerator

def test_alpha_rhythm():
    sfreq = 250
    n_channels = 2
    sig = OscillationGenerator.alpha_rhythm(duration=2.0, sfreq=sfreq, n_channels=n_channels)
    assert sig.sampling_rate == sfreq
    assert sig.data.shape == (500, 2)
    
def test_p300_wave():
    sfreq = 250
    n_channels = 1
    sig = CognitiveGenerator.p300_wave(sfreq=sfreq, n_channels=n_channels, latency=0.3)
    assert sig.sampling_rate == sfreq
    assert sig.data.shape == (250, 1)
    
    # Peak should be exactly at 0.3s (index 75)
    peak_idx = np.argmax(sig.data[:, 0])
    assert peak_idx == 75

def test_hardware_saturation():
    sfreq = 100
    n_channels = 1
    sig = OscillationGenerator.pure_sine(duration=1.0, sfreq=sfreq, n_channels=n_channels, freq=10.0, amplitude=10.0)
    clipped = ArtifactGenerator.hardware_saturation(sig, clip_min=-5.0, clip_max=5.0)
    assert np.max(clipped.data) == 5.0
    assert np.min(clipped.data) == -5.0
