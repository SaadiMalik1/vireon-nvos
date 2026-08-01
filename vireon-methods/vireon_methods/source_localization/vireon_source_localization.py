import numpy as np
from vireon_core.contracts.plugin import ScientificContractViolation

class VireonMinimumNorm:
    """MNE inverse solution.
    
    Reference: Hämäläinen & Ilmoniemi (1994). Interpreting magnetic fields of
    the brain: minimum norm estimates. Medical & Biological Engineering &
    Computing, 32(1), 35-42.
    """
    def __init__(self, leadfield: np.ndarray, noise_cov: np.ndarray = None,
                 snr: float = 3.0):
        if not isinstance(leadfield, np.ndarray):
            leadfield = np.array(leadfield)
        self.L = leadfield
        
        if noise_cov is None:
            self.noise_cov = np.eye(self.L.shape[0])
        else:
            if not isinstance(noise_cov, np.ndarray):
                noise_cov = np.array(noise_cov)
            self.noise_cov = noise_cov
            
        self.snr = snr
        self.lambda2 = 1.0 / (snr ** 2)
        
    def fit(self, X: np.ndarray) -> np.ndarray:
        """X: (n_sensors, n_samples). Returns source estimate (n_sources, n_samples)."""
        if not isinstance(X, np.ndarray):
            X = np.array(X)
            
        if np.any(np.isnan(X)) or np.any(np.isinf(X)):
            raise ScientificContractViolation(
                "Signal contains NaN or Inf values.",
                violated_assumption="finite_values",
                details="NaN or Inf detected.",
                remediation="Clean data."
            )
            
        # 1. Compute inverse operator: W = L.T @ (L @ L.T + lambda2 * noise_cov)^-1
        # Gamma = L @ L.T + lambda2 * noise_cov
        Gamma = self.L @ self.L.T + self.lambda2 * self.noise_cov
        
        # W = L.T @ Gamma^-1
        # To compute W without explicitly inverting Gamma:
        # Gamma.T @ W.T = L
        # W.T = solve(Gamma.T, L)
        # W = solve(Gamma.T, L).T
        W_T = np.linalg.solve(Gamma.T, self.L)
        W = W_T.T
        
        # 2. Apply: source = W @ X
        return W @ X
