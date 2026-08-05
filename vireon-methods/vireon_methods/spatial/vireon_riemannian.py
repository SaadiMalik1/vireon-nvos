"""Riemannian Geometry Minimum Distance to Mean (MDM) Spatial Classifier.

Reference: Barachant, A., Bonnet, S., Congedo, M., & Jutten, C. (2012). Multiclass brain-computer 
interface classification by Riemannian geometry. IEEE Transactions on Biomedical Engineering, 59(4), 920-928.
DOI: 10.1109/TBME.2011.2172216
"""
import numpy as np
from typing import Optional


class VireonRiemannianMDM:
    """Minimum Distance to Mean classifier on Riemannian manifold of SPD matrices."""
    
    def __init__(self):
        self.class_means_ = {}
        self.classes_ = None

    def _riemannian_distance(self, A: np.ndarray, B: np.ndarray) -> float:
        """Compute Riemannian distance d_R(A, B) = || logm(A^{-1/2} B A^{-1/2}) ||_F."""
        # Using symmetric log determinant approximation for speed/robustness
        vals = np.linalg.eigvalsh(np.linalg.pinv(A) @ B)
        vals = np.maximum(vals, 1e-10)
        return float(np.sqrt(np.sum(np.log(vals) ** 2)))

    def fit(self, X: np.ndarray, y: np.ndarray):
        """Fit class mean covariance matrices on SPD manifold."""
        self.classes_ = np.unique(y)
        for c in self.classes_:
            covs = [np.cov(epoch) for epoch in X[y == c]]
            self.class_means_[c] = np.mean(covs, axis=0)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict class labels for test epochs using minimum Riemannian distance."""
        preds = []
        for epoch in X:
            cov = np.cov(epoch)
            dists = [self._riemannian_distance(cov, self.class_means_[c]) for c in self.classes_]
            preds.append(self.classes_[np.argmin(dists)])
        return np.array(preds)

    def fit_transform(self, X: np.ndarray, y: np.ndarray) -> np.ndarray:
        self.fit(X, y)
        return self.predict(X)
