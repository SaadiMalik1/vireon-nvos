"""Mutual Information Information-Theoretic Functional Connectivity Estimator.

Reference: Kraskov, A., Stogbauer, H., & Grassberger, P. (2004). Estimating mutual information.
Physical Review E, 69(6), 066138. DOI: 10.1103/PhysRevE.69.066138
"""
import numpy as np
from typing import Optional
from scipy.spatial import cKDTree
from scipy.special import digamma
from vireon_core.contracts.plugin import ScientificContractViolation


class VireonMutualInformation:
    """Mutual Information estimator using Kraskov k-NN method (KSG estimator).

    Reference: Kraskov, Stogbauer, Grassberger (2004).
    "Estimating mutual information." Phys Rev E. 69:066138.
    DOI: 10.1103/PhysRevE.69.066138

    Implements Estimator 1 (epsilon-ball approach).
    """

    def __init__(self, k: int = 4, n_neighbors: Optional[int] = None, n_bins: Optional[int] = None):
        """
        Args:
            k: number of nearest neighbors for distance computation (default 4, per paper).
            n_neighbors: alias for k (sklearn compatibility).
            n_bins: legacy fallback argument.
        """
        if n_neighbors is not None:
            k = n_neighbors
        if k < 1:
            raise ValueError(f"k must be >= 1, got {k}")
        self.k = k

    def _validate(self, x: np.ndarray, y: np.ndarray) -> None:
        if x.ndim != 1 or y.ndim != 1:
            raise ScientificContractViolation(
                plugin_id="vk:Method:MutualInformation",
                violated_assumption="input_shape",
                details=f"x and y must be 1D; got shapes {x.shape}, {y.shape}",
                remediation="Flatten x and y to 1D arrays",
            )
        if x.shape != y.shape:
            raise ScientificContractViolation(
                plugin_id="vk:Method:MutualInformation",
                violated_assumption="shape_match",
                details=f"x and y must have same length; got {x.shape} vs {y.shape}",
                remediation="Ensure x and y have matching dimensions",
            )
        if len(x) < self.k + 1:
            raise ScientificContractViolation(
                plugin_id="vk:Method:MutualInformation",
                violated_assumption="minimum_samples",
                details=f"Need at least k+1={self.k+1} samples; got {len(x)}",
                remediation="Provide signals with length >= k+1",
            )
        if np.any(np.isnan(x)) or np.any(np.isnan(y)) or np.any(np.isinf(x)) or np.any(np.isinf(y)):
            raise ScientificContractViolation(
                plugin_id="vk:Method:MutualInformation",
                violated_assumption="finite_values",
                details="x or y contains NaN or Inf values",
                remediation="Clean data or impute NaN/Inf values",
            )

    def compute(self, x: np.ndarray, y: np.ndarray) -> float:
        """Compute mutual information I(X;Y) using Kraskov k-NN estimator.

        Args:
            x: 1D array of samples from random variable X.
            y: 1D array of samples from random variable Y (same length as x).

        Returns:
            Mutual information in nats (natural log).
        """
        self._validate(x, y)
        x = np.asarray(x, dtype=np.float64)
        y = np.asarray(y, dtype=np.float64)
        n = len(x)

        # Add tiny jitter to break exact ties in distance
        rng = np.random.default_rng(42)
        x_j = x + 1e-10 * rng.standard_normal(n)
        y_j = y + 1e-10 * rng.standard_normal(n)

        # Build joint space tree
        joint = np.column_stack([x_j, y_j])
        tree_joint = cKDTree(joint)
        distances, _ = tree_joint.query(joint, k=self.k + 1, p=np.inf)
        eps = distances[:, self.k]

        tree_x = cKDTree(x_j.reshape(-1, 1))
        tree_y = cKDTree(y_j.reshape(-1, 1))

        # Strictly less than eps[i]
        n_x = np.array([len(tree_x.query_ball_point([x_j[i]], eps[i] - 1e-15, p=np.inf)) - 1 for i in range(n)])
        n_y = np.array([len(tree_y.query_ball_point([y_j[i]], eps[i] - 1e-15, p=np.inf)) - 1 for i in range(n)])

        mi = digamma(self.k) - np.mean(digamma(n_x + 1) + digamma(n_y + 1)) + digamma(n)

        return float(max(0.0, mi))

    def compute_matrix(self, data: np.ndarray) -> np.ndarray:
        """Compute pairwise MI matrix for multivariate data (n_channels, n_samples)."""
        if data.ndim != 2:
            raise ScientificContractViolation(
                plugin_id="vk:Method:MutualInformation",
                violated_assumption="input_shape",
                details=f"data must be 2D (channels, samples); got {data.shape}",
                remediation="Ensure input array has 2 dimensions (n_channels, n_samples)",
            )
        n_ch = data.shape[0]
        mi_matrix = np.zeros((n_ch, n_ch))
        for i in range(n_ch):
            for j in range(i + 1, n_ch):
                mi = self.compute(data[i], data[j])
                mi_matrix[i, j] = mi
                mi_matrix[j, i] = mi
        return mi_matrix
