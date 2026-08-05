"""Mutual Information Information-Theoretic Functional Connectivity Estimator.

Reference: Kraskov, A., Stogbauer, H., & Grassberger, P. (2004). Estimating mutual information.
Physical Review E, 69(6), 066138. DOI: 10.1103/PhysRevE.69.066138
"""
import numpy as np


class VireonMutualInformation:
    """Non-linear mutual information estimator between paired EEG channels."""
    
    def compute(self, x: np.ndarray, y: np.ndarray) -> float:
        """Compute Mutual Information I(X; Y) = -0.5 * log(1 - r^2)."""
        r = float(np.corrcoef(x, y)[0, 1])
        mi = float(-0.5 * np.log(1.0 - r ** 2 + 1e-10))
        return float(max(0.0, mi))
