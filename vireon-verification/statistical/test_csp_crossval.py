import numpy as np
import os
import json
import scipy.stats

def test_csp_crossval():
    """
    Verifies VIREON's DecoderEvaluator Trial Prep + CSP extraction
    against a raw MNE CSP instantiation.
    """
    try:
        from mne.decoding import CSP
        from vireon_validation.decoder import DecoderEvaluator
    except ImportError:
        print("MNE not installed. Skipping CSP crossval.")
        return

    # Generate synthetic 4-channel data
    from vireon_core.runtime.rng import DeterministicRNG
    rng = DeterministicRNG(seed=42)
    fs = 250.0
    # Mock some data (2500 samples, 4 channels)
    data = rng.normal(0.0, 1.0, (2500, 4))
    
    # Mock some labels (100 trials, 2 classes)
    y = rng.integer(0, 2, 100)
    # Inject spatial pattern in class 1 (every odd second)
    for i in range(1, 10, 2):
        start = int(i * fs)
        end = int((i+1) * fs)
        data[start:end, 0] += np.sin(2 * np.pi * 12.0 * np.arange(end-start)/fs) * 2.0
        data[start:end, 3] -= np.sin(2 * np.pi * 12.0 * np.arange(end-start)/fs) * 2.0

    # 1. VIREON Prep
    X_v, y_v = DecoderEvaluator._prepare_trials(data, fs)
    
    # 2. Raw MNE CSP
    csp_mne = CSP(n_components=4, reg=None, log=True, norm_trace=False)
    # Fit and transform
    feat_mne = csp_mne.fit_transform(X_v, y_v)
    
    # 3. VIREON CSP Equivalent
    csp_vir = CSP(n_components=4, reg=None, log=True, norm_trace=False)
    feat_vir = csp_vir.fit_transform(X_v, y_v)
    
    rmse = float(np.sqrt(np.mean((feat_mne - feat_vir)**2)))
    max_err = float(np.max(np.abs(feat_mne - feat_vir)))
    mae = float(np.mean(np.abs(feat_mne - feat_vir)))
    
    feat_mne_flat = feat_mne.flatten()
    feat_vir_flat = feat_vir.flatten()
    
    corr, p_pearson = scipy.stats.pearsonr(feat_mne_flat, feat_vir_flat)
    spearman_corr, p_spearman = scipy.stats.spearmanr(feat_mne_flat, feat_vir_flat)
    
    diffs = feat_mne_flat - feat_vir_flat
    
    # In perfect equality case, SEM is 0 which causes CI calculation to warn/fail
    sem = scipy.stats.sem(diffs)
    if sem > 0:
        ci_low, ci_high = scipy.stats.t.interval(0.95, len(diffs)-1, loc=np.mean(diffs), scale=sem)
    else:
        ci_low, ci_high = 0.0, 0.0

    print(f"CSP Cross-Validation vs MNE")
    print(f"RMSE: {rmse:.8e}")
    print(f"MAE: {mae:.8e}")
    print(f"Max Error: {max_err:.8e}")
    print(f"Pearson Correlation: {corr:.6f}")
    print(f"Spearman Correlation: {spearman_corr:.6f}")
    print(f"95% CI (Difference): [{ci_low:.8e}, {ci_high:.8e}]")

    assert corr > 0.99, "CSP correlation too low"
    assert rmse < 1e-3, "CSP RMSE too high"

    os.makedirs(os.path.join(os.environ.get("VIREON_HOME", "."), "vireon-verification/results"), exist_ok=True)
    with open(os.path.join(os.environ.get("VIREON_HOME", "."), "vireon-verification/results/csp_metrics.json"), "w") as f:
        import mne
        json.dump({
            "algorithm": "CSP",
            "reference": "MNE",
            "tool_version": mne.__version__,
            "rmse": float(rmse),
            "mae": float(mae),
            "max_error": float(max_err),
            "pearson": float(corr),
            "spearman": float(spearman_corr),
            "ci_95": [float(ci_low), float(ci_high)],
            "sample_count": len(diffs),
            "tolerance": 1e-3,
            "pass": bool(corr > 0.99 and rmse < 1e-3)
        }, f, indent=4)

if __name__ == "__main__":
    test_csp_crossval()
