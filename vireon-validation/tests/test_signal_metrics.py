import sys
import os
import unittest
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from vireon_validation.metrics import (
    compute_snr_raw,
    _compute_band_power_raw,
    detect_powerline_artifact,
    detect_p300_erp,
    generate_signal_metrics,
    BANDS,
)
from vireon_core.contracts.base import IMeasurement


class TestSNR(unittest.TestCase):
    def test_known_snr_with_explicit_noise(self):
        """SNR with explicit noise estimate should be computable."""
        t = np.linspace(0, 1.0, 250, endpoint=False)
        signal = np.sin(2 * np.pi * 10.0 * t).astype(np.float32) * 10.0
        noise = np.random.default_rng(42).normal(0, 0.1, size=250).astype(np.float32)
        snr = compute_snr_raw(signal, noise)
        self.assertGreater(snr, 30.0)

    def test_noisy_signal_lower_snr(self):
        """Adding significant noise should reduce SNR."""
        t = np.linspace(0, 1.0, 250, endpoint=False)
        signal = np.sin(2 * np.pi * 10.0 * t).astype(np.float32)
        noise = np.random.default_rng(42).normal(0, 2.0, size=250).astype(np.float32)
        snr_clean = compute_snr_raw(signal, np.zeros_like(signal))
        snr_noisy = compute_snr_raw(signal + noise, noise)
        self.assertGreater(snr_clean, snr_noisy)

    def test_multichannel(self):
        """SNR should work on 2D arrays."""
        t = np.linspace(0, 1.0, 250, endpoint=False)
        data = np.column_stack([
            np.sin(2 * np.pi * 10.0 * t),
            np.sin(2 * np.pi * 20.0 * t),
        ]).astype(np.float32)
        snr = compute_snr_raw(data)
        self.assertIsInstance(snr, float)


class TestBandPower(unittest.TestCase):
    def test_alpha_band_detection(self):
        """A 10Hz sine should have most power in the alpha band."""
        t = np.linspace(0, 2.0, 500, endpoint=False)
        signal = np.sin(2 * np.pi * 10.0 * t).astype(np.float32)
        alpha_power = _compute_band_power_raw(signal, 250.0, BANDS["alpha"])
        beta_power = _compute_band_power_raw(signal, 250.0, BANDS["beta"])
        self.assertGreater(alpha_power, beta_power * 5)

    def test_beta_band_detection(self):
        """A 20Hz sine should have most power in the beta band."""
        t = np.linspace(0, 2.0, 500, endpoint=False)
        signal = np.sin(2 * np.pi * 20.0 * t).astype(np.float32)
        alpha_power = _compute_band_power_raw(signal, 250.0, BANDS["alpha"])
        beta_power = _compute_band_power_raw(signal, 250.0, BANDS["beta"])
        self.assertGreater(beta_power, alpha_power * 5)


class TestPowerlineDetection(unittest.TestCase):
    def test_detects_50hz(self):
        t = np.linspace(0, 2.0, 500, endpoint=False)
        signal = (np.sin(2 * np.pi * 10.0 * t) * 5.0 + 
                  np.sin(2 * np.pi * 50.0 * t) * 20.0).astype(np.float32)
        self.assertTrue(detect_powerline_artifact(signal, 250.0, 50.0))

    def test_no_false_positive(self):
        t = np.linspace(0, 2.0, 500, endpoint=False)
        signal = np.sin(2 * np.pi * 10.0 * t).astype(np.float32)
        self.assertFalse(detect_powerline_artifact(signal, 250.0, 50.0))


class TestGenerateSignalMetrics(unittest.TestCase):
    def test_full_metrics_from_provider_data(self):
        """generate_signal_metrics should return all expected keys with uncertainty."""
        t = np.linspace(0, 2.0, 500, endpoint=False)
        data = np.column_stack([
            np.sin(2 * np.pi * 10.0 * t) * 25.0,
            np.sin(2 * np.pi * 20.0 * t) * 10.0,
        ]).astype(np.float32)
        
        provider_data = {"data": data, "sample_rate": 250.0, "num_channels": 2}
        metrics = generate_signal_metrics(provider_data)
        
        metric_names = []
        for m in metrics:
            metric_names.append(m.metric_name)

        self.assertIn("snr_db", metric_names)
        self.assertIn("alpha_band_power", metric_names)
        self.assertIn("beta_band_power", metric_names)
        self.assertIn("powerline_50hz_detected", metric_names)
        
        # Verify uncertainty fields for SNR
        snr_metric = next(m for m in metrics if m.metric_name == "snr_db")
        self.assertIsInstance(snr_metric.value, float)
        self.assertIsNotNone(snr_metric.variance)
        self.assertIsNotNone(snr_metric.confidence_interval_95)
        self.assertEqual(len(snr_metric.confidence_interval_95), 2)

    def test_empty_for_non_numpy(self):
        metrics = generate_signal_metrics({"data": "mock_string"})
        self.assertEqual(metrics, [])


class TestP300Detection(unittest.TestCase):
    def test_detects_p300_in_synthesized_data(self):
        from vireon_models.providers.datasets import SyntheticDataGenerator
        gen = SyntheticDataGenerator(seed=42)
        with_p300 = gen.generate_eeg_stream(duration_sec=1.0, include_p300=True, noise_level=0.0)
        without_p300 = gen.generate_eeg_stream(duration_sec=1.0, include_p300=False, noise_level=0.0)
        
        self.assertTrue(detect_p300_erp(with_p300, event_onset_sec=0.0))
        self.assertFalse(detect_p300_erp(without_p300, event_onset_sec=0.0))

if __name__ == "__main__":
    unittest.main()
