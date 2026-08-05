"""Mutual Information Information-Theoretic Functional Connectivity Estimator.

Reference: Kraskov, A., Stogbauer, H., & Grassberger, P. (2004). Estimating mutual information.
Physical Review E, 69(6), 066138. DOI: 10.1103/PhysRevE.69.066138
"""
import numpy as np


class VireonMutualInformation:
    """Non-linear Mutual Information estimator using 2D Histogram Binning and Kraskov entropy formulations."""
    
    def __init__(self, n_bins: int = 10):
        self.n_bins = n_bins

    def compute(self, x: np.ndarray, y: np.ndarray) -> float:
        """Compute Mutual Information I(X; Y) using 2D joint histogram binning estimator."""
        # Compute 2D joint histogram and marginal 1D probability distributions
        hist_2d, _, _ = np.histogram2d(x, y, bins=self.n_bins)
        p_xy = hist_2d / float(np.sum(hist_2d))
        
        p_x = np.sum(p_xy, axis=1)
        p_y = np.sum(p_xy, axis=0)
        
        # Outer product of marginals p_x * p_y
        p_x_p_y = np.outer(p_x, p_y)
        
        # Compute I(X;Y) = sum p(x,y) * log( p(x,y) / (p(x)p(y)) )
        nonzero_mask = p_xy > 0
        mi = np.sum(p_xy[nonzero_mask] * np.log(p_xy[nonzero_mask] / p_x_p_y[nonzero_mask]))
        
        return float(max(0.0, mi))
