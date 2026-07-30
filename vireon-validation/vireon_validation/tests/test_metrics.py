import unittest
import numpy as np

from vireon_validation.metrics import compute_snr_raw, detect_p300_erp

class TestMetrics(unittest.TestCase):
    def test_snr_pure_signal(self):
        """Test SNR on a perfectly noise-free signal vs heavily noisy signal."""
        t = np.linspace(0, 1, 1000)
        pure_signal = np.sin(2 * np.pi * 10 * t).reshape(-1, 1)
        
        # SNR of pure sine wave should be very high (or inf theoretically, but practically high)
        snr_pure = compute_snr_raw(pure_signal)
        self.assertGreater(snr_pure, 10.0) # at least 10 dB
        
    def test_snr_noisy_signal(self):
        """Test SNR with explicit high noise."""
        rng = np.random.default_rng(42)
        noise = rng.normal(0, 5, (1000, 1))
        
        snr_noise = compute_snr_raw(noise)
        # Random noise should have near 0 or negative SNR because there's no coherent signal
        self.assertLess(snr_noise, 5.0)

    def test_detect_p300_present(self):
        """Test P300 detection when exactly shaped pulse exists at target latency."""
        # P300 is expected at ~300ms.
        # Data shape: (samples, channels)
        sample_rate = 250.0
        t = np.linspace(0, 1, int(sample_rate))
        data = np.zeros((int(sample_rate), 1))
        
        # Inject Gaussian pulse at 300ms (0.3s)
        pulse = 10.0 * np.exp(-0.5 * ((t - 0.3) / 0.05)**2)
        data[:, 0] = pulse
        
        provider_data = {
            "data": data,
            "sample_rate": sample_rate,
            "duration_sec": 1.0
        }
        
        # Event onset is 0.0 (the stimulus starts at 0, P300 happens 300ms later)
        detected = detect_p300_erp(provider_data, event_onset_sec=0.0)
        self.assertTrue(detected)
        
    def test_detect_p300_absent(self):
        """Test P300 detection when there is no pulse."""
        sample_rate = 250.0
        data = np.zeros((int(sample_rate), 1))
        
        provider_data = {
            "data": data,
            "sample_rate": sample_rate,
            "duration_sec": 1.0
        }
        
        detected = detect_p300_erp(provider_data, event_onset_sec=0.0)
        self.assertFalse(detected)

if __name__ == '__main__':
    unittest.main()
