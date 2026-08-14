"""Delorme & Makeig (2004) EEGLAB ICA Pipeline Test.

Reference: Delorme, A., & Makeig, S. (2004). EEGLAB: an open source toolbox for analysis
of single-trial EEG dynamics including independent component analysis. Journal of Neuroscience Methods,
134(1), 9-21. DOI: 10.1016/j.jneumeth.2003.10.009
Dataset: ERP CORE
Subfield: cognitive
"""
import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.spatial.vireon_ica import VireonICA


def test_delorme_2004():
    """EEGLAB artifact component identification and matrix reconstruction."""
    DeterministicRNG(seed=2004)
    t = np.linspace(0, 2, 500)
    # EEG + EOG artifact (blink peak)
    eeg = np.sin(2 * np.pi * 10 * t)
    blink = 5.0 * np.exp(-((t - 1.0) ** 2) / 0.01)
    X = np.vstack([eeg + 0.5 * blink, 0.2 * eeg + blink]).T

    ica = VireonICA(n_components=2)
    sources = ica.fit_transform(X)

    rec = sources[:, :1] @ ica.mixing_[:1, :]
    assert rec.shape == (500, 2), f"Reconstruction shape mismatch {rec.shape}"

    # Strengthened falsifiable assertion: ICA's full forward+backward
    # reconstruction must match the original signal near-perfectly (modulo
    # numerical noise) because ICA is invertible. The correct reconstruction
    # formula is X ≈ sources @ mixing_.T + mean (mixing_ is the (n_features,
    # n_components) mixing matrix A such that X_centered = sources @ A.T).
    full_rec = sources @ ica.mixing_.T + ica.mean_
    rec_err = float(np.linalg.norm(X - full_rec) / np.linalg.norm(X))
    assert rec_err < 0.1, (
        f"ICA full reconstruction relative error {rec_err:.4f} not < 0.1 — "
        "ICA mixing matrix does not invert the unmixing transform"
    )

    # Strengthened falsifiable assertion: the recovered ICA components must be
    # approximately uncorrelated (a defining statistical property of ICA —
    # independent components are necessarily uncorrelated). For a correct
    # ICA decomposition, the absolute off-diagonal entry of the source
    # correlation matrix must be well below 0.1.
    corr = np.corrcoef(sources.T)
    off_diag = float(corr[0, 1])
    assert abs(off_diag) < 0.1, (
        f"ICA recovered components correlated (|r|={abs(off_diag):.3f} >= 0.1) — "
        "decomposition failed to find independent sources"
    )

    # At least one component must dominate the mixing-energy spectrum (the
    # blink artifact has 5x the EEG amplitude, so its source must contribute
    # most of the signal energy after decomposition). The per-source energy
    # contribution is var(source_i) * ||mixing_[:, i]||^2; since FastICA
    # whitens sources to unit variance, the dominant source is the one with
    # the largest column norm in mixing_.
    col_norms_sq = np.sum(ica.mixing_ ** 2, axis=0)  # (n_components,)
    max_energy_ratio = float(np.max(col_norms_sq) / np.sum(col_norms_sq))
    assert max_energy_ratio > 0.6, (
        f"ICA dominant-source energy ratio {max_energy_ratio:.3f} not > 0.6 — "
        "no single source dominates (decomposition failed to separate blink from EEG)"
    )


if __name__ == "__main__":
    test_delorme_2004()
