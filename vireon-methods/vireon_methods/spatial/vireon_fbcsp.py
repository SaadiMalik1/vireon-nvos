"""Filter Bank Common Spatial Pattern (FBCSP) Spatial Filter.

Reference: Ang, K. K., Chin, Z. Y., Zhang, H., & Guan, C. (2012). Filter bank common spatial pattern (FBCSP)
in brain-computer interface. Proceedings of the International Joint Conference on Neural Networks, 2390-2397.
DOI: 10.1109/IJCNN.2012.6252486
"""
import numpy as np
from typing import List, Tuple, Optional
from vireon_methods.filtering.vireon_iir import VireonIIR
from vireon_methods.spatial.vireon_csp import VireonCSP
from vireon_core.contracts.plugin import ScientificContractViolation


class VireonFBCSP:
    """Filter Bank Common Spatial Patterns (Blankertz 2008).

    Applies band-pass filters per frequency band, then runs CSP on each
    band's filtered signal. Concatenates log-variance features across bands.
    """

    def __init__(
        self,
        n_components: int = 2,
        bands: Optional[List[Tuple[float, float]]] = None,
        filter_order: int = 4,
    ):
        if bands is None:
            # Standard BCI Competition IV-2a filter bank
            bands = [(4.0, 8.0), (8.0, 12.0), (12.0, 16.0), (16.0, 24.0), (24.0, 32.0)]
        self.bands = [(float(l), float(h)) for l, h in bands]
        self.n_components = n_components
        self.filter_order = filter_order
        self._fs = None
        self._filters = []  # One VireonIIR per band
        self._csps = []     # One VireonCSP per band
        self._fitted = False

    def _validate_input(self, X: np.ndarray, fs: Optional[float] = None) -> None:
        if X.ndim != 3:
            raise ScientificContractViolation(
                plugin_id="vk:Method:FBCSP",
                violated_assumption="input_shape",
                details=f"X must be 3D (epochs, channels, samples); got shape {X.shape}",
                remediation="Ensure input array has 3 dimensions (n_epochs, n_channels, n_samples)",
            )
        if np.any(np.isnan(X)) or np.any(np.isinf(X)):
            raise ScientificContractViolation(
                plugin_id="vk:Method:FBCSP",
                violated_assumption="finite_values",
                details="X contains NaN or Inf values",
                remediation="Clean data or impute NaN/Inf values",
            )
        if fs is not None:
            for low, high in self.bands:
                if low >= high:
                    raise ValueError(f"Band ({low}, {high}) has low >= high")
                if high >= fs / 2:
                    raise ValueError(f"Band high {high} Hz exceeds Nyquist {fs/2} Hz")

    def fit(self, X: np.ndarray, y: np.ndarray, fs: float = 250.0) -> "VireonFBCSP":
        """Fit FBCSP. X: (epochs, channels, samples). y: labels. fs: sample rate."""
        self._fs = fs
        self._validate_input(X, fs)

        self._filters = []
        self._csps = []
        for (low, high) in self.bands:
            # Create and apply band-pass filter for this band
            filt = VireonIIR(
                fs=fs,
                cutoff=(low, high),
                btype="bandpass",
                order=self.filter_order,
            )
            # Filter each epoch: apply along time axis
            X_band = np.array([filt.apply(epoch) for epoch in X])
            # Fit CSP on filtered data
            csp = VireonCSP(n_components=self.n_components)
            csp.fit(X_band, y)
            self._filters.append(filt)
            self._csps.append(csp)

        self._fitted = True
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        """Transform X to FBCSP features: (epochs, n_bands * n_components)."""
        if not self._fitted:
            raise ScientificContractViolation(
                plugin_id="vk:Method:FBCSP",
                violated_assumption="fitted_state",
                details="VireonFBCSP.transform called before fit()",
                remediation="Call fit(X, y) before calling transform(X)",
            )
        self._validate_input(X, self._fs)
        band_feats = []
        for filt, csp in zip(self._filters, self._csps):
            X_band = np.array([filt.apply(epoch) for epoch in X])
            feats = csp.transform(X_band)
            band_feats.append(feats)
        return np.hstack(band_feats)

    def fit_transform(self, X: np.ndarray, y: np.ndarray, fs: float = 250.0) -> np.ndarray:
        """Convenience: fit then transform."""
        self.fit(X, y, fs=fs)
        return self.transform(X)
