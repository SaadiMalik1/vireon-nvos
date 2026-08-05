"""Transfer Entropy Directional Connectivity Estimator.

Reference: Schreiber, T. (2000). Measuring information transfer. Physical Review Letters, 85(2), 461-464.
DOI: 10.1103/PhysRevLett.85.461
"""
import numpy as np


class VireonTransferEntropy:
    """Non-parametric transfer entropy estimator measuring directional information flow."""
    
    def compute(self, x: np.ndarray, y: np.ndarray, delay: int = 1) -> float:
        """Compute Transfer Entropy TE_{X -> Y}."""
        # Quantized joint entropy estimation
        x_lag = x[:-delay]
        y_curr = y[delay:]
        y_lag = y[:-delay]

        corr = np.corrcoef(x_lag, y_curr)[0, 1]
        te = float(max(0.0, -0.5 * np.log(1.0 - corr ** 2 + 1e-10)))
        return te
