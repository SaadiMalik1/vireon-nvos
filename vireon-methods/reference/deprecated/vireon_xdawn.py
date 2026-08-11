"""DEPRECATED: This native implementation is retained for reference only.
VIREON now delegates to mature libraries (MOABB, MNE, scipy, sklearn, pyriemann).
Use the corresponding adapter in vireon_moabb.adapters instead.

This file will be removed in v2.1.0.
"""
"""xDAWN Spatial Filtering for Event-Related Potential (ERP) Signal Enhancement.

Reference: Rivet, B., Cecotti, H., Souloumiac, A., Maby, E., & Mattout, J. (2009). xDAWN algorithm 
to enhance evoked potentials: application to brain-computer interfaces. IEEE Transactions on Biomedical Engineering, 56(8), 2035-2043.
DOI: 10.1109/TBME.2009.2019709
"""
import numpy as np


class VireonxDAWN:
    """xDAWN spatial filter for enhancing target signal-to-noise ratio in ERPs."""
    
    def __init__(self, n_filter: int = 2):
        self.n_filter = n_filter
        self.filters_ = None

    def fit(self, X: np.ndarray, y: np.ndarray):
        """Fit spatial filters projecting ERP target signal onto high SNR subspace."""
        n_epochs, n_channels, n_samples = X.shape
        target_epochs = X[y == 1]
        evoked = np.mean(target_epochs, axis=0)

        # Average covariance and target signal covariance
        cov_tot = np.mean([np.cov(ep) for ep in X], axis=0)
        cov_target = np.cov(evoked)

        # Generalized eigenvalue problem
        vals, vecs = np.linalg.eigh(np.linalg.pinv(cov_tot) @ cov_target)
        idx = np.argsort(vals)[::-1]
        self.filters_ = vecs[:, idx[:self.n_filter]].T
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        """Project multi-channel signal epochs through xDAWN spatial filters."""
        return np.array([self.filters_ @ ep for ep in X])
