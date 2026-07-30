import unittest
import numpy as np

from vireon_validation.decoder import DecoderEvaluator

class TestDecoder(unittest.TestCase):
    def test_decoder_perfect_separation(self):
        """Test CSP+LDA decoder on perfectly separable data."""
        # Create 10 seconds of 4-channel data at 250Hz.
        sample_rate = 250.0
        n_samples = int(10 * sample_rate)
        n_channels = 4
        
        # Create an array of 0s.
        data = np.zeros((n_samples, n_channels))
        
        # We will create 1-second trials. 10 trials total.
        labels = np.zeros(n_samples)
        
        # Trial 0, 2, 4, 6, 8 (Class 0): Sine wave on channels 0 and 1
        # Trial 1, 3, 5, 7, 9 (Class 1): Sine wave on channels 2 and 3
        t = np.linspace(0, 1, int(sample_rate), endpoint=False)
        sine_wave = np.sin(2 * np.pi * 10 * t)
        
        # Add slight noise to prevent singular covariance matrices (log(0) = -inf in CSP)
        rng = np.random.default_rng(42)
        data += rng.normal(0, 0.01, (n_samples, n_channels))
        
        for i in range(10):
            start = int(i * sample_rate)
            end = int((i + 1) * sample_rate)
            
            if i % 2 == 0:
                labels[start:end] = 0
                data[start:end, 0] = sine_wave
                data[start:end, 1] = sine_wave
            else:
                labels[start:end] = 1
                data[start:end, 2] = sine_wave
                data[start:end, 3] = sine_wave
                
        metrics = DecoderEvaluator.evaluate(data, sample_rate, labels)
        
        # It should perfectly classify this trivial task.
        self.assertGreaterEqual(metrics["decoder_accuracy"], 0.9)
        self.assertGreaterEqual(metrics["decoder_roc_auc"], 0.9)

    def test_decoder_random_noise(self):
        """Test CSP+LDA decoder on random noise (should be ~chance level)."""
        sample_rate = 250.0
        n_samples = int(20 * sample_rate)
        n_channels = 4
        
        rng = np.random.default_rng(42)
        data = rng.normal(0, 1, (n_samples, n_channels))
        
        labels = np.zeros(n_samples)
        for i in range(20):
            start = int(i * sample_rate)
            end = int((i + 1) * sample_rate)
            labels[start:end] = i % 2
            
        metrics = DecoderEvaluator.evaluate(data, sample_rate, labels)
        
        # Accuracy should be near chance level (0.5 for 2 classes)
        self.assertLessEqual(metrics["decoder_accuracy"], 0.8) # Allow some variance due to small sample size
        # ROC AUC should also be near 0.5
        self.assertLessEqual(metrics["decoder_roc_auc"], 0.8)

if __name__ == '__main__':
    unittest.main()
