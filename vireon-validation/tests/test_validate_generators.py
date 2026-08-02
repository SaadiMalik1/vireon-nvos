import unittest
import numpy as np
from vireon_validation.benchmarks.validate_generators import ValidatorEngine

class TestValidateGenerators(unittest.TestCase):
    def test_synthetic_alpha_generation(self):
        engine = ValidatorEngine(seed=42)
        signal = engine.generate_synthetic_alpha(n_samples=500)
        self.assertEqual(len(signal), 500)
        self.assertFalse(np.any(np.isnan(signal)))

    def test_ks_validation_returns_honest_stats(self):
        engine = ValidatorEngine(seed=42)
        res = engine.validate_alpha_generator()
        self.assertIn("ks_stat", res)
        self.assertIn("p_value", res)
        self.assertIn("effect_size", res)
        self.assertIn("verdict", res)
        self.assertIsInstance(res["ks_stat"], float)
        self.assertIsInstance(res["p_value"], float)

if __name__ == "__main__":
    unittest.main()
