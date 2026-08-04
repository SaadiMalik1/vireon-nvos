"""Khan et al. (2022) Frontal Alpha Asymmetry Emotion Recognition Test.

Reference: Khan, A., et al. (2022). Deep learning-based emotion recognition using frontal alpha 
asymmetry features from EEG signals. Biomedical Signal Processing and Control, 73, 103348.
DOI: 10.1016/j.bspc.2021.103348
Dataset: ERP CORE
Subfield: cognitive
"""
import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.spectral.vireon_welch import VireonWelch


def test_khan_2022():
    """Frontal Alpha Asymmetry (FAA) score calculation log(F4_alpha) - log(F3_alpha)."""
    rng = DeterministicRNG(seed=2022)
    fs = 250.0
    t = np.arange(0, 4, 1 / fs)

    # Positive valence: higher left frontal activity -> lower left alpha (F3) power than right alpha (F4)
    f3_sig = 0.8 * np.sin(2 * np.pi * 10.0 * t) + rng.normal(0, 0.1, len(t))
    f4_sig = 2.0 * np.sin(2 * np.pi * 10.0 * t) + rng.normal(0, 0.1, len(t))

    welch = VireonWelch(fs=fs, nperseg=256)
    f, psd_f3 = welch.compute(f3_sig)
    _, psd_f4 = welch.compute(f4_sig)

    alpha_mask = (f >= 8.0) & (f <= 12.0)
    alpha_f3 = float(np.sum(psd_f3[alpha_mask]))
    alpha_f4 = float(np.sum(psd_f4[alpha_mask]))

    faa_score = float(np.log(alpha_f4) - np.log(alpha_f3))

    assert faa_score > 0.0, f"Frontal Alpha Asymmetry score {faa_score:.3f} <= 0.0"


if __name__ == "__main__":
    test_khan_2022()
