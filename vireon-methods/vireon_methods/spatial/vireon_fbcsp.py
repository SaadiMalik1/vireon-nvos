"""Filter Bank Common Spatial Pattern (FBCSP) Spatial Filter.

Reference: Ang, K. K., Chin, Z. Y., Zhang, H., & Guan, C. (2012). Filter bank common spatial pattern (FBCSP)
in brain-computer interface. Proceedings of the International Joint Conference on Neural Networks, 2390-2397.
DOI: 10.1109/IJCNN.2012.6252486
"""
import numpy as np
from vireon_methods.spatial.vireon_csp import VireonCSP


class VireonFBCSP:
    """Filter Bank CSP extracting multi-frequency sub-band spatial features."""
    
    def __init__(self, n_components: int = 2, bands: list = None):
        self.n_components = n_components
        self.bands = bands or [(4, 8), (8, 12), (12, 16), (16, 24), (24, 32)]
        self.csps = [VireonCSP(n_components=n_components) for _ in self.bands]

    def fit_transform(self, X: np.ndarray, y: np.ndarray) -> np.ndarray:
        """Extract multi-band CSP features concatenated across filter banks."""
        band_feats = []
        for csp in self.csps:
            feats = csp.fit_transform(X, y)
            band_feats.append(feats)
        return np.hstack(band_feats)
