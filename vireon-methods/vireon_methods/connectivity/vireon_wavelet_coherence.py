"""Wavelet Coherence Functional Connectivity Estimator using Continuous Wavelet Transform (CWT Morlet Wavelet).

Reference: Lachaux, J. P., Rodriguez, E., Martinerie, J., & Varela, F. J. (1999).
Measuring phase synchrony in brain signals. Human Brain Mapping, 8(4), 194-208.
DOI: 10.1002/(SICI)1097-0193(1999)8:4<194::AID-HBM4>3.0.CO;2-C
"""
import numpy as np
import scipy.signal


class VireonWaveletCoherence:
    """Wavelet-based time-frequency cross-coherence estimator using Morlet CWT wavelets."""
    
    def __init__(self, freqs: np.ndarray = None, w0: float = 6.0):
        self.freqs = freqs if freqs is not None else np.linspace(4.0, 30.0, 10)
        self.w0 = w0

    def _cwt_morlet(self, sig: np.ndarray, fs: float) -> np.ndarray:
        """Compute Morlet Continuous Wavelet Transform (CWT) matrix."""
        n_samples = len(sig)
        cwt_matrix = np.zeros((len(self.freqs), n_samples), dtype=complex)
        t = np.arange(-n_samples // 2, n_samples // 2) / fs
        
        for idx, f in enumerate(self.freqs):
            # Complex Morlet wavelet equation: psi(t) = pi^(-1/4) * exp(i 2pi f t) * exp(-t^2 / 2)
            morlet_wavelet = np.pi**(-0.25) * np.exp(1j * 2 * np.pi * f * t) * np.exp(-t**2 / 2.0)
            cwt_matrix[idx] = scipy.signal.fftconvolve(sig, morlet_wavelet, mode="same")
            
        return cwt_matrix

    def compute(self, data: np.ndarray, fs: float = 250.0) -> np.ndarray:
        """Compute pairwise Morlet CWT wavelet coherence matrix across EEG channels."""
        n_channels = data.shape[0]
        coherence_matrix = np.eye(n_channels)
        
        # Compute CWT for each channel
        cwts = [self._cwt_morlet(data[ch], fs) for ch in range(n_channels)]
        
        for i in range(n_channels):
            for j in range(i + 1, n_channels):
                # Cross-wavelet spectrum S_xy and auto-spectra S_xx, S_yy
                W_x = cwts[i]
                W_y = cwts[j]
                W_xy = W_x * np.conj(W_y)
                
                # Cross-coherence magnitude squared
                numerator = np.abs(np.mean(W_xy)) ** 2
                denominator = (np.mean(np.abs(W_x) ** 2) * np.mean(np.abs(W_y) ** 2)) + 1e-10
                coh_val = float(np.clip(numerator / denominator, 0.0, 1.0))
                
                coherence_matrix[i, j] = coh_val
                coherence_matrix[j, i] = coh_val
                
        return coherence_matrix
