import numpy as np
import os
import scipy.signal
import scipy.stats
from vireon_validation.metrics import compute_psd

def test_psd_crossval():
    """
    Verifies VIREON's PSD implementation against SciPy's periodogram.
    """
    # Load reference signal
    ref_dir = os.path.join(os.environ.get("VIREON_HOME", "."), "tests", "fixtures", "references")
    if not os.path.exists(ref_dir):
        ref_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "tests", "fixtures", "references")
    if os.path.exists(os.path.join(ref_dir, "test_signal.npy")):
        signal = np.load(os.path.join(ref_dir, "test_signal.npy"))
    else:
        # Generate synthetic sine signal fallback
        fs = 250.0
        t = np.arange(0, 4, 1 / fs)
        signal = np.sin(2 * np.pi * 10 * t)
    fs = 250.0

    from vireon_methods.spectral.vireon_welch import VireonWelch
    v_freqs, v_psd = VireonWelch(fs=fs, nperseg=512).compute(signal)
    s_freqs, s_psd = scipy.signal.welch(signal, fs=fs, nperseg=512, window='hann', noverlap=256, detrend='constant', scaling='density')

    assert np.allclose(v_freqs, s_freqs), "Frequency axes must match"
    assert np.allclose(v_psd, s_psd, rtol=1e-7), "PSD must match within 1e-7"

    rmse = float(np.sqrt(np.mean((v_psd - s_psd)**2)))
    max_err = float(np.max(np.abs(v_psd - s_psd)))
    mae = float(np.mean(np.abs(v_psd - s_psd)))
    corr, p_pearson = scipy.stats.pearsonr(v_psd, s_psd)
    spearman_corr, p_spearman = scipy.stats.spearmanr(v_psd, s_psd)
    
    # 95% CI of the difference
    diffs = v_psd - s_psd
    
    sem = scipy.stats.sem(diffs)
    if sem > 0:
        ci_low, ci_high = scipy.stats.t.interval(0.95, len(diffs)-1, loc=np.mean(diffs), scale=sem)
    else:
        ci_low, ci_high = 0.0, 0.0

    print(f"PSD Cross-Validation vs SciPy")
    print(f"RMSE: {rmse:.8e}")
    print(f"MAE: {mae:.8e}")
    print(f"Max Error: {max_err:.8e}")
    print(f"Pearson Correlation: {corr:.6f}")
    print(f"Spearman Correlation: {spearman_corr:.6f}")
    print(f"95% CI (Difference): [{ci_low:.8e}, {ci_high:.8e}]")

    assert corr > 0.99, "PSD correlation too low"
    assert rmse < 1e-3, "PSD RMSE too high"

    # Write metrics to a dashboard-friendly file
    os.makedirs(os.path.join(os.environ.get("VIREON_HOME", "."), "vireon-verification/results"), exist_ok=True)
    with open(os.path.join(os.environ.get("VIREON_HOME", "."), "vireon-verification/results/psd_metrics.json"), "w") as f:
        import json
        json.dump({
            "algorithm": "Welch PSD",
            "reference": "SciPy (Welch)",
            "tool_version": scipy.__version__,
            "rmse": float(rmse),
            "mae": float(mae),
            "max_error": float(max_err),
            "pearson": float(corr),
            "spearman": float(spearman_corr),
            "ci_95": [float(ci_low), float(ci_high)],
            "sample_count": len(diffs),
            "tolerance": 1e-7,
            "pass": bool(corr > 0.99 and rmse < 1e-3)
        }, f, indent=4)

if __name__ == "__main__":
    test_psd_crossval()
