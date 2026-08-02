import numpy as np
from scipy import linalg
from typing import Optional

class VireonCSP:
    """
    Native VIREON implementation of Common Spatial Patterns (CSP).
    Calculates spatial filters via generalized eigenvalue decomposition.
    """
    def __init__(self, n_components: int = 4):
        self.n_components = n_components
        self.filters_: Optional[np.ndarray] = None
        self.patterns_: Optional[np.ndarray] = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> "VireonCSP":
        """
        Fit CSP filters on epoched data (epochs, channels, times).
        """
        classes = np.unique(y)
        if len(classes) != 2:
            raise ValueError(f"CSP requires exactly 2 classes, got {len(classes)}")

        # Calculate average normalized covariance per class
        covs = []
        for c in classes:
            X_c = X[y == c]
            cov_c = np.zeros((X.shape[1], X.shape[1]), dtype=np.float64)
            for trial in X_c:
                trial_cov = np.cov(trial)
                trace = np.trace(trial_cov)
                if trace > 0:
                    trial_cov /= trace
                cov_c += trial_cov
            cov_c /= len(X_c)
            covs.append(cov_c)

        cov_0, cov_1 = covs[0], covs[1]
        
        # Generalized eigenvalue problem: cov_0 * w = lambda * (cov_0 + cov_1) * w
        w, v = linalg.eigh(cov_0, cov_0 + cov_1)
        
        # Sort eigenvectors by eigenvalues
        ix = np.argsort(w)
        # Select first and last components
        n_half = self.n_components // 2
        selected = np.concatenate([ix[:n_half], ix[-n_half:]])
        
        self.filters_ = v[:, selected].T
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        """
        Apply CSP filters and return log-variance features.
        """
        if self.filters_ is None:
            raise ValueError("CSP model not fitted.")
        
        n_epochs = X.shape[0]
        n_filters = self.filters_.shape[0]
        features = np.zeros((n_epochs, n_filters), dtype=np.float64)
        
        for i in range(n_epochs):
            projected = self.filters_ @ X[i]
            var = np.var(projected, axis=1)
            # Log normalized variance
            sum_var = np.sum(var)
            if sum_var > 0:
                var /= sum_var
            features[i] = np.log(np.maximum(var, 1e-12))
            
        return features

    def fit_transform(self, X: np.ndarray, y: np.ndarray) -> np.ndarray:
        return self.fit(X, y).transform(X)
