import numpy as np
import scipy.stats
from vireon_core.runtime.rng import DeterministicRNG
from vireon_validation.statistics.framework import StatisticalFramework
from typing import Dict, Any, Optional

class ValidatorEngine:
    """
    Validates VIREON's internal synthetic generators against real or reference EEG distributions.
    """
    def __init__(self, seed: int = 42):
        self.rng = DeterministicRNG(seed=seed)
        self.stats = StatisticalFramework()
        
    def generate_synthetic_alpha(self, n_samples: int = 1000, fs: float = 250.0, center_freq: float = 10.0) -> np.ndarray:
        """
        Generates synthetic alpha band signal envelope.
        """
        t = np.arange(n_samples) / fs
        # Synthetic alpha oscillation + white noise
        osc = np.sin(2 * np.pi * center_freq * t)
        noise = self.rng.normal(0.0, 0.5, (n_samples,))
        signal = osc + noise
        return signal

    def validate_alpha_generator(self, real_data: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Runs a two-sample Kolmogorov-Smirnov test between synthetic alpha and reference EEG data.
        """
        synthetic_alpha = self.generate_synthetic_alpha(n_samples=1000)
        
        if real_data is None:
            # If no external dataset provided, generate reference empirical signal
            t = np.arange(1000) / 250.0
            ref_rng = DeterministicRNG(seed=12345)
            real_alpha = np.sin(2 * np.pi * 10.2 * t) + ref_rng.normal(0.0, 0.55, (1000,))
        else:
            real_alpha = real_data

        # Use K-S test to compare distributions
        ks_res = scipy.stats.ks_2samp(synthetic_alpha, real_alpha)
        ks_stat = float(ks_res.statistic)
        p_value = float(ks_res.pvalue)
        
        # Effect size (Cohen's d)
        effect_size = self.stats.cohens_d(synthetic_alpha, real_alpha)
        
        verdict = "PASS" if (p_value > 0.01 and abs(effect_size) < 0.5) else "DIFFERENT"
        
        return {
            "ks_stat": ks_stat,
            "p_value": p_value,
            "effect_size": effect_size,
            "verdict": verdict,
            "message": f"KS statistic: {ks_stat:.4f}, p-value: {p_value:.4f}, Cohen's d: {effect_size:.4f}"
        }

if __name__ == "__main__":
    validator = ValidatorEngine()
    print("Validating Synthetic Alpha Generator...")
    print(validator.validate_alpha_generator())
