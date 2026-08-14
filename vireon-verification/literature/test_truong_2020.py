"""Truong et al. (2020) STFT Seizure Prediction Test.

Reference: Truong, N. D., Nguyen, A. D., Kuhlmann, L., Bonyadi, M. R., Yang, J., Ippolito, S., & Kavehei, O. (2020).
Convolutional neural networks for seizure prediction using intracranial and scalp electroencephalogram.
Expert Systems with Applications, 143, 113842. DOI: 10.1016/j.eswa.2020.113842
Dataset: CHB-MIT
Subfield: epilepsy
"""
import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.spectral.vireon_stft import VireonSTFT


def test_truong_2020():
    """STFT spectrogram extraction for pre-ictal vs inter-ictal seizure detection."""
    rng = DeterministicRNG(seed=2020)
    fs = 256.0
    t = np.arange(0, 4, 1 / fs)

    # Pre-ictal high gamma power surge (50 Hz)
    preictal_sig = 2.0 * np.sin(2 * np.pi * 50.0 * t) + rng.normal(0, 0.2, len(t))

    stft = VireonSTFT(fs=fs, nperseg=64, noverlap=32)
    f, t_ax, Zxx = stft.compute(preictal_sig)

    gamma_mask = (f >= 45.0) & (f <= 55.0)
    high_gamma_mag = float(np.mean(np.abs(Zxx[gamma_mask, :])))

    assert high_gamma_mag > 0.5, f"Pre-ictal STFT gamma magnitude {high_gamma_mag:.3f} <= 0.5"


if __name__ == "__main__":
    test_truong_2020()
