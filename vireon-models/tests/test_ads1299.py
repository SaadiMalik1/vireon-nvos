import numpy as np
from vireon_models.hardware import ADS1299
from vireon_core.runtime.rng import DeterministicRNG

def test_ads1299_noise():
    """Verify ADS1299 adds ~1 µVpp noise at 250 SPS."""
    rng = DeterministicRNG(42)
    ads = ADS1299(gain=24, sample_rate=250, rng=rng)
    
    # Process zero signal
    signal = np.zeros((10000, 4))
    output = ads.process(signal)
    
    # 99.9% of values should be within +/- 0.5 µV (1.0 µVpp)
    # The noise RMS is 1.0 / 6.6 = 0.1515 µV
    std_dev = np.std(output)
    
    assert 0.13 < std_dev < 0.17, f"Noise std dev {std_dev} not in expected range"

def test_ads1299_quantization():
    """Verify ADS1299 quantizes the output."""
    rng = DeterministicRNG(42)
    ads = ADS1299(gain=24, sample_rate=250, rng=rng)
    
    # A tiny signal that should be quantized
    signal = np.linspace(-1, 1, 1000).reshape(-1, 1)
    output = ads.process(signal)
    
    # Unique values should be spaced by roughly lsb_uv / gain
    # lsb_uv = 4.5 / (24 * 2**23) * 1e6 = 0.02235 µV
    # Quantized steps at input-referred scale = lsb_uv / gain = 0.02235 / 24 = 0.00093 µV
    step = ads.lsb_uv / ads.gain
    
    diffs = np.diff(np.sort(np.unique(output)))
    
    # Most non-zero differences should be multiples of the step size
    # Because of noise, all unique values are quantized to step multiples
    for d in diffs:
        if d > 1e-9:
            ratio = d / step
            assert np.isclose(ratio, np.round(ratio), atol=1e-3), "Output is not quantized to LSB multiples"
