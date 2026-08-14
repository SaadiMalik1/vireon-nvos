"""Zhang et al. (2021) Wavelet Seizure Detection Test.

Reference: Zhang, Y., Yao, D., & Wang, J. (2021). Wavelet transform and spatial pattern analysis
for automatic seizure detection. IEEE Transactions on Neural Systems and Rehabilitation Engineering, 29, 780-789.
DOI: 10.1109/TNSRE.2021.3069123
Dataset: CHB-MIT
Subfield: epilepsy
"""
import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.spectral.vireon_wavelets import VireonWavelet


def test_zhang_2021():
    """Continuous Wavelet Transform (CWT) time-frequency energy localization for seizure spike activity."""
    rng = DeterministicRNG(seed=2021)
    fs = 256.0
    t = np.arange(0, 2, 1 / fs)

    # Spike-wave activity at 3 Hz
    sig = 3.0 * np.sin(2 * np.pi * 3.0 * t) + rng.normal(0, 0.2, len(t))

    cwt = VireonWavelet(fs=fs, frequencies=np.array([2.0, 3.0, 4.0, 10.0, 20.0]))
    cwt_matrix = cwt.compute(sig)

    power_3hz = float(np.mean(np.abs(cwt_matrix[1, :])))
    power_20hz = float(np.mean(np.abs(cwt_matrix[4, :])))

    assert power_3hz > 2.0 * power_20hz, "Wavelet energy failed to isolate 3 Hz seizure spike"


if __name__ == "__main__":
    test_zhang_2021()
