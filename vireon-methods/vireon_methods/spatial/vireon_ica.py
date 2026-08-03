import numpy as np
from vireon_core.contracts.plugin import ScientificContractViolation
from vireon_core.runtime.rng import DeterministicRNG

class VireonICA:
    """Native FastICA implementation.
    
    Reference: Hyvärinen, A., & Oja, E. (2000). Independent Component Analysis: 
    Algorithms and Applications. Neural Networks, 13(4-5), 411-430.
    DOI: 10.1016/S0893-6080(00)00026-5
    """
    
    def __init__(self, n_components: int = None, max_iter: int = 200, 
                 tol: float = 1e-4, fun: str = "logcosh", whiten: str = "unit-variance"):
        self.n_components = n_components
        self.max_iter = max_iter
        self.tol = tol
        self.fun = fun
        self.whiten = whiten
        self.components_ = None
        self._mixing = None
        self._mean = None
        self._whitening_matrix = None
        self._unwhitening_matrix = None
        
    def _sym_decorrelation(self, W: np.ndarray) -> np.ndarray:
        """Symmetric decorrelation: W <- (W * W.T)^{-1/2} * W"""
        # We can use SVD: W = U * S * V.T -> W_sym = U * V.T
        U, S, Vt = np.linalg.svd(W, full_matrices=False)
        return U @ Vt

    def fit(self, X: np.ndarray) -> "VireonICA":
        """X shape: (n_samples, n_features). Returns self."""
        if not isinstance(X, np.ndarray):
            X = np.array(X)
            
        if np.any(np.isnan(X)) or np.any(np.isinf(X)):
            raise ScientificContractViolation(
                "Data contains NaN or Inf values.",
                violated_assumption="finite_values",
                details="NaN or Inf detected.",
                remediation="Clean data."
            )
            
        n_samples, n_features = X.shape
        n_components = self.n_components if self.n_components is not None else n_features
        
        if n_components > min(n_samples, n_features):
            raise ScientificContractViolation(
                "n_components must be <= min(n_samples, n_features).",
                violated_assumption="identifiability",
                details=f"n_components={n_components}, n_samples={n_samples}, n_features={n_features}",
                remediation="Reduce n_components."
            )
            
        self.n_components = n_components
        
        # 1. Center X
        self._mean = np.mean(X, axis=0)
        X_centered = X - self._mean
        
        # 2. Whiten (SVD on data or covariance)
        # Using SVD on data: X = U * S * V.T
        U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
        
        # Take top n_components
        U = U[:, :n_components]
        S = S[:n_components]
        Vt = Vt[:n_components, :]
        
        # Whitening matrix (maps X -> X_white)
        # X_white = X_centered @ W_whiten
        # Since X_centered = U * S * V.T
        # We want var(X_white) = I
        K = (Vt.T / S) * np.sqrt(n_samples)
        
        # Unwhitening matrix (maps X_white -> X)
        K_inv = (Vt.T * S) / np.sqrt(n_samples)
        
        X_white = X_centered @ K
        # Transpose to shape (n_components, n_samples) for easier dot products
        X_white = X_white.T
        
        # 3. Initialize W random orthogonal
        rng = DeterministicRNG(seed=42)
        W = rng.normal(0, 1, size=(n_components, n_components))
        W = self._sym_decorrelation(W)
        
        # 4. Iterate
        for i in range(self.max_iter):
            # wx shape: (n_components, n_samples)
            wx = W @ X_white
            
            if self.fun == "logcosh":
                g = np.tanh(wx)
                g_prime = 1.0 - g**2
            elif self.fun == "exp":
                g = wx * np.exp(-(wx**2) / 2.0)
                g_prime = (1.0 - wx**2) * np.exp(-(wx**2) / 2.0)
            elif self.fun == "cube":
                g = wx**3
                g_prime = 3.0 * wx**2
            else:
                raise ValueError("Unknown fun type")
                
            # Update rule for symmetric decorrelation
            # E[X * g(W.T X)] - E[g'(W.T X)] * W
            W_new = (g @ X_white.T) / n_samples - np.mean(g_prime, axis=1)[:, np.newaxis] * W
            
            W_new = self._sym_decorrelation(W_new)
            
            # Check convergence
            lim = max(abs(abs(np.diag(W_new @ W.T)) - 1))
            W = W_new
            if lim < self.tol:
                break
                
        # 5. Store components
        # Unmixing matrix for centered X is W @ K.T
        unmixing = W @ K.T
        self.components_ = unmixing
        
        # Mixing matrix is K_inv @ W.T
        self._mixing = K_inv @ W.T
        
        return self
        
    def transform(self, X: np.ndarray) -> np.ndarray:
        """Returns independent components (n_samples, n_components)."""
        if self.components_ is None:
            raise ValueError("Model not fitted yet.")
        X_centered = X - self._mean
        return X_centered @ self.components_.T
        
    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        self.fit(X)
        return self.transform(X)
        
    @property
    def mixing_(self) -> np.ndarray:
        """Mixing matrix (n_features, n_components)."""
        if self._mixing is None:
            raise ValueError("Model not fitted yet.")
        return self._mixing

    @property
    def mean_(self) -> np.ndarray:
        """Mean of features across samples."""
        if self._mean is None:
            raise ValueError("Model not fitted yet.")
        return self._mean
