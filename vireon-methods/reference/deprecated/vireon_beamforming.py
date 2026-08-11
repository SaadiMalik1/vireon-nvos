"""DEPRECATED: This native implementation is retained for reference only.
VIREON now delegates to mature libraries (MOABB, MNE, scipy, sklearn, pyriemann).
Use the corresponding adapter in vireon_moabb.adapters instead.

This file will be removed in v2.1.0.
"""
import numpy as np
from vireon_core.contracts.plugin import ScientificContractViolation

class VireonLCMV:
    """LCMV beamformer.
    
    Reference: Van Veen & Buckley (1988). Beamforming: A Versatile Approach to
    Spatial Filtering. IEEE ASSP Magazine, 5(2), 4-24.
    """
    def __init__(self, leadfield: np.ndarray, reg: float = 0.05):
        """leadfield shape: (n_sensors, n_sources)."""
        if not isinstance(leadfield, np.ndarray):
            leadfield = np.array(leadfield)
        self.leadfield = leadfield
        self.reg = reg
        self.cov = None
        self.weights = None
        
    def fit(self, X: np.ndarray) -> "VireonLCMV":
        """X shape: (n_sensors, n_samples). Compute data covariance C."""
        if not isinstance(X, np.ndarray):
            X = np.array(X)
            
        if np.any(np.isnan(X)) or np.any(np.isinf(X)):
            raise ScientificContractViolation(
                "Signal contains NaN or Inf values.",
                violated_assumption="finite_values",
                details="NaN or Inf detected.",
                remediation="Clean data."
            )
            
        self.cov = np.cov(X)
        self.cov += self.reg * np.eye(self.cov.shape[0])
        
        cov_inv = np.linalg.pinv(self.cov)
        n_sources = self.leadfield.shape[1]
        n_sensors = self.leadfield.shape[0]
        
        self.weights = np.zeros((n_sensors, n_sources))
        
        for j in range(n_sources):
            l_j = self.leadfield[:, j]
            # w_j = (C^-1 @ L_j) / (L_j.T @ C^-1 @ L_j)
            numerator = cov_inv @ l_j
            denominator = l_j.T @ cov_inv @ l_j
            if denominator == 0:
                self.weights[:, j] = 0
            else:
                self.weights[:, j] = numerator / denominator
            
        return self
        
    def apply(self, X: np.ndarray) -> np.ndarray:
        """Returns source estimate (n_sources, n_samples)."""
        if self.weights is None:
            raise ValueError("Beamformer not fitted. Call fit() first.")
            
        if not isinstance(X, np.ndarray):
            X = np.array(X)
            
        if np.any(np.isnan(X)) or np.any(np.isinf(X)):
            raise ScientificContractViolation(
                "Signal contains NaN or Inf values.",
                violated_assumption="finite_values",
                details="NaN or Inf detected.",
                remediation="Clean data."
            )
            
        # source_j = w_j.T @ X
        return self.weights.T @ X
