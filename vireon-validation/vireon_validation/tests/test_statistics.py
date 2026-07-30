import unittest
import numpy as np

from vireon_validation.statistics import compute_cohens_d, compute_permutation_test, compute_bootstrap_ci

class TestStatistics(unittest.TestCase):
    def test_cohens_d_exact(self):
        """Test Cohen's d against a known mathematically exact calculation."""
        # Setup: Two groups of known means and standard deviation
        # Group 1: Mean = 10, Variance = 4, N = 10
        # Group 2: Mean = 8, Variance = 4, N = 10
        # Pooled StdDev = sqrt(4) = 2.0
        # Cohen's d = (10 - 8) / 2.0 = 1.0
        
        # Create synthetic arrays with these exact properties
        rng = np.random.default_rng(42)
        
        x = rng.standard_normal(10)
        x = (x - np.mean(x)) / np.std(x, ddof=1) # mean 0, std 1
        x = x * 2.0 + 10.0 # mean 10, std 2 (variance 4)
        
        y = rng.standard_normal(10)
        y = (y - np.mean(y)) / np.std(y, ddof=1) # mean 0, std 1
        y = y * 2.0 + 8.0 # mean 8, std 2 (variance 4)
        
        d = compute_cohens_d(x, y)
        self.assertAlmostEqual(d, 1.0, places=4)
        
    def test_cohens_d_zero(self):
        """Test Cohen's d when groups are identical."""
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([1, 2, 3, 4, 5])
        
        d = compute_cohens_d(x, y)
        self.assertAlmostEqual(d, 0.0, places=4)
        
    def test_permutation_test_significant(self):
        """Test permutation test on clearly separated distributions."""
        x = np.random.normal(10, 1, 50)
        y = np.random.normal(0, 1, 50)
        
        p_val = compute_permutation_test(x, y, n_permutations=100)
        self.assertLess(p_val, 0.05)
        
    def test_permutation_test_nonsignificant(self):
        """Test permutation test on identically distributed arrays."""
        rng = np.random.default_rng(42)
        x = rng.normal(0, 1, 50)
        y = rng.normal(0, 1, 50)
        
        p_val = compute_permutation_test(x, y, n_permutations=1000)
        self.assertGreater(p_val, 0.05)
        
    def test_bootstrap_ci(self):
        """Test bootstrap confidence interval for mean."""
        x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        mean_estimate, var, ci = compute_bootstrap_ci(x, np.mean, n_resamples=1000)
        
        self.assertAlmostEqual(mean_estimate, 3.0, places=4)
        self.assertLess(ci[0], 3.0)
        self.assertGreater(ci[1], 3.0)

if __name__ == '__main__':
    unittest.main()
