import pytest
import numpy as np
from vireon_devices.hardware import ADCModel, AmplifierModel, ADS1299

def test_adc_quantization():
    # 24-bit ADC, v_ref = 4.5V, gain = 24
    adc = ADCModel(bit_depth=24, v_ref_uv=4500000.0, gain=24.0)
    
    # Create a smooth continuous signal
    signal = np.linspace(-100.0, 100.0, 1000)
    
    quantized = adc.process(signal)
    
    # The quantized signal should be very close to the original (high resolution)
    assert np.allclose(signal, quantized, atol=1.0)
    
    # But it should have discrete steps, so difference between adjacent points isn't always smooth
    diff = np.diff(quantized)
    # LSB is approx 0.011 uV
    assert abs(adc.lsb - 0.01117) < 0.001
    
def test_adc_saturation():
    adc = ADCModel(bit_depth=24, v_ref_uv=4500000.0, gain=24.0)
    
    # Signal way beyond dynamic range (v_max is approx 93750 uV)
    signal = np.array([200000.0, -200000.0])
    
    quantized = adc.process(signal)
    
    assert np.isclose(quantized[0], adc.v_max)
    assert np.isclose(quantized[1], adc.v_min)

def test_amplifier_noise():
    amp = AmplifierModel(noise_rms_uv=5.0, powerline_amp_uv=0.0, seed=42)
    signal = np.zeros((1000, 1))
    
    amplified = amp.process(signal, sample_rate=250.0)
    
    # Standard deviation should be close to the injected RMS noise
    assert abs(np.std(amplified) - 5.0) < 0.5
    
def test_ads1299_integration():
    device = ADS1299()
    signal = np.zeros((1000, 8))
    
    processed = device.process(signal, sample_rate=250.0)
    
    assert processed.shape == (1000, 8)
    assert np.std(processed) > 0.0  # Noise was added
