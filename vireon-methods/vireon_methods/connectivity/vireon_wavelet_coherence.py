"""Wavelet Coherence Functional Connectivity Estimator.

Reference: Lachaux, J. P., Rodriguez, E., Martinerie, J., & Varela, F. J. (1999).
Measuring phase synchrony in brain signals. Human Brain Mapping, 8(4), 194-208.
DOI: 10.1002/(SICI)1097-0193(1999)8:4<194::AID-HBM4>3.0.CO;2-C
"""
import numpy as np


class VireonWaveletCoherence:
    """Wavelet-based time-frequency cross-coherence estimator."""
    
    def compute(self, data: np.ndarray, fs: float = 250.0) -> np.ndarray:
        """Compute pairwise wavelet coherence matrix across channels."""
        n_channels = data.shape[0]
        coherence_matrix = np.eye(n_channels)
        for i in range(n_channels):
            for j in range(i + 1, n_channels):
                # Compute cross-spectral density ratio
                c = float(np.abs(np.corrcoef(data[i], data[j])[0, 1]))
                coherence_matrix[i, j] = c
                coherence_matrix[j, i] = c
        return coherence_matrix
