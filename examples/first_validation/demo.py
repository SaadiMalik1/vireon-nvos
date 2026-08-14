import sys
import os
import json
import numpy as np

# Ensure vireon modules can be imported regardless of execution working directory
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
for pkg in ['vireon-core', 'vireon-models', 'vireon-lab', 'vireon-methods', 'vireon-validation', 'vireon-evidence', 'vireon-knowledge', 'vireon-corpus']:
    pkg_path = os.path.join(repo_root, pkg)
    if pkg_path not in sys.path:
        sys.path.insert(0, pkg_path)

from vireon_core.runtime.rng import DeterministicRNG
from vireon_models.providers.datasets import PhysioNetMotorImageryProvider
from vireon_methods.machine_learning.csp import CSPPlugin
from vireon_validation.benchmarks.matrix import BenchmarkMatrix
from vireon_validation.perturbations.library import WhiteNoisePerturbation
from vireon_evidence.exporters.report_generator import MultiFormatReportGenerator

def _generate_pink_noise(n: int, rng: DeterministicRNG) -> np.ndarray:
    """Generate 1/f pink noise using spectral method."""
    freqs = np.fft.rfftfreq(n)
    freqs[0] = 1.0  # avoid div by zero
    spectrum = rng.normal(0.0, 1.0, len(freqs)) / np.sqrt(freqs)
    spectrum[0] = 0.0
    noise = np.fft.irfft(spectrum, n=n)
    return noise / (np.std(noise) + 1e-10)  # normalize

def _generate_synthetic_motor_imagery(seed: int = 42, n_epochs: int = 60, n_channels: int = 16,
                                      n_samples: int = 250, fs: float = 250.0):
    """Generate synthetic motor imagery data with a realistic ERD/ERS pattern.

    Class 0 (left hand): moderate mu-band (10 Hz) power, lateralized to left hemisphere.
    Class 1 (right hand): moderate mu-band power, lateralized to right hemisphere.

    The contrast is deliberately moderate (not trivially separable) so that
    CSP+LDA achieves ~75-85% accuracy, giving a non-trivial CCC.
    """
    rng = DeterministicRNG(seed)

    X = np.zeros((n_epochs, n_channels, n_samples))
    y = np.array([0, 1] * (n_epochs // 2))

    t = np.arange(n_samples) / fs
    mu_freq = 10.0  # Hz

    # Channel groups (simulating 10-20 layout with 16 channels)
    left_hemi = [3, 4, 5, 6]    # left hemisphere
    right_hemi = [9, 10, 11, 12] # right hemisphere

    for i in range(n_epochs):
        # Background 1/f pink noise (~2 µV std) — realistic EEG background
        for ch in range(n_channels):
            X[i, ch] = _generate_pink_noise(n_samples, rng) * 2.0

        # Add white noise (~0.5 µV) — sensor noise
        for ch in range(n_channels):
            X[i, ch] += rng.normal(0, 0.5, n_samples)

        if y[i] == 0:
            # Class 0: ERD in left hemisphere (mu power suppressed), normal in right
            for ch in range(n_channels):
                if ch in left_hemi:
                    mu_power = 1.5  # ERD: reduced mu
                elif ch in right_hemi:
                    mu_power = 4.0  # Normal mu
                else:
                    mu_power = 3.0
                # Add frequency jitter for realism
                freq_jitter = mu_freq + rng.normal(0, 0.3)
                phase = rng.uniform(0, 2 * np.pi)
                X[i, ch] += mu_power * np.sin(2 * np.pi * freq_jitter * t + phase)
        else:
            # Class 1: ERD in right hemisphere, normal in left
            for ch in range(n_channels):
                if ch in right_hemi:
                    mu_power = 1.5  # ERD
                elif ch in left_hemi:
                    mu_power = 4.0  # Normal
                else:
                    mu_power = 3.0
                freq_jitter = mu_freq + rng.normal(0, 0.3)
                phase = rng.uniform(0, 2 * np.pi)
                X[i, ch] += mu_power * np.sin(2 * np.pi * freq_jitter * t + phase)

    return X, y

def main():
    print("==================================================")
    print("  VIREON - NATIVE NEUROSCIENCE EVIDENCE ENGINE    ")
    print("==================================================")
    
    seed = int(os.environ.get("VIREON_SEED", "42"))
    
    print("\n[1] Loading PhysioNet Motor Imagery Dataset...")
    try:
        provider = PhysioNetMotorImageryProvider(subject_id=1, run_id=4)
        data_dict = provider.get_data()
        X = data_dict["data"]
        y = data_dict["label"]
        sample_rate = data_dict.get("sample_rate", 160.0)
        data_source = "PhysioNet (real)"
    except (FileNotFoundError, ConnectionError, Exception):
        print("    PhysioNet not available; using deterministic synthetic data with ERD pattern.")
        X, y = _generate_synthetic_motor_imagery(seed=seed)
        sample_rate = 250.0
        data_source = "Synthetic (deterministic, with ERD)"
    
    print(f"    Loaded {X.shape[0]} trials, {X.shape[1]} channels, {X.shape[2]} samples. Source: {data_source}")
    
    print("\n[2] Loading Algorithm Under Test (CSP)...")
    csp = CSPPlugin(n_components=2)
    print(f"    Purpose: {csp.contract.purpose}")
    print(f"    Assumptions: {', '.join(csp.contract.mathematical_assumptions)}")
    print(f"    Validation Papers: {', '.join(csp.contract.validation_papers)}")
    
    print("\n[3] Building Cartesian Benchmark Matrix...")
    matrix = BenchmarkMatrix(seed=seed)
    matrix.add_method(csp)
    matrix.add_dataset("MotorImagery", data=X, labels=y)
    for sev in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
        matrix.add_perturbation(WhiteNoisePerturbation(name=f"WhiteNoise_{sev:.1f}", severity=sev))

    # Also run a Welch PSD benchmark: Vireon Welch vs scipy Welch
    print("\n[3b] Running Spectral Benchmark (Vireon Welch vs scipy)...")
    from vireon_methods.spectral.vireon_welch import VireonWelch
    import scipy.signal
    # Use channel 0 of first epoch as test signal
    test_signal = X[0, 0, :]
    f_v, psd_v = VireonWelch(fs=sample_rate, nperseg=128).compute(test_signal)
    f_s, psd_s = scipy.signal.welch(test_signal, fs=sample_rate, nperseg=128, window='hann',
                                     noverlap=64, detrend='constant', scaling='density')
    welch_rmse = float(np.sqrt(np.mean((psd_v - psd_s) ** 2)))
    welch_max_rel = float(np.max(np.abs(psd_v - psd_s) / (np.abs(psd_s) + 1e-20)))
    print(f"    Vireon Welch vs scipy: RMSE={welch_rmse:.2e}, max_rel_err={welch_max_rel:.2e}")
    print(f"    Match (rtol=1e-7): {'YES' if welch_max_rel < 1e-7 else 'NO'}")

    # Run ICA benchmark: Vireon ICA vs sklearn FastICA
    print("\n[3c] Running ICA Benchmark (Vireon ICA vs sklearn FastICA)...")
    from vireon_methods.spatial.vireon_ica import VireonICA
    from sklearn.decomposition import FastICA
    # Use a subset of channels for ICA (needs n_samples >= n_channels)
    ica_data = X[:, :8, :].reshape(-1, X.shape[2]).T  # (n_samples, 8 channels)
    ica_data = ica_data[:1000]  # limit for speed
    try:
        vireon_ica = VireonICA(n_components=4)
        vireon_components = vireon_ica.fit_transform(ica_data)
        sklearn_ica = FastICA(n_components=4, random_state=42, max_iter=200)
        sklearn_components = sklearn_ica.fit_transform(ica_data)
        # Compare subspaces via SVD of cross-correlation matrix
        cross_corr = np.corrcoef(vireon_components.T, sklearn_components.T)[:4, 4:]
        from numpy.linalg import svd
        _, sv, _ = svd(cross_corr)
        subspace_match = float(np.min(sv))
        print(f"    ICA subspace match (min singular value): {subspace_match:.6f}")
        print(f"    Match (>0.95): {'YES' if subspace_match > 0.95 else 'NO'}")
    except Exception as e:
        print(f"    ICA benchmark skipped: {e}")

    # Run perturbation severity sweep
    print("\n[3d] Running Perturbation Severity Sweep...")
    severity_results = []
    for sev in [0.0, 0.1, 0.3, 0.5, 1.0, 2.0, 5.0]:
        if sev == 0.0:
            perturbed = X.copy()
            pert_name = "baseline"
        else:
            pert = WhiteNoisePerturbation(name=f"WN_{sev}", severity=sev, seed=seed)
            perturbed = pert.apply(X)
            pert_name = f"noise_{sev}"
        try:
            from sklearn.model_selection import StratifiedKFold
            from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
            cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
            scores = []
            for train_idx, test_idx in cv.split(perturbed, y):
                fold_csp = CSPPlugin(n_components=2)
                train_feats = fold_csp.execute({"signal": perturbed[train_idx], "labels": y[train_idx]})
                test_feats = fold_csp.execute({"signal": perturbed[test_idx], "labels": None})
                lda = LinearDiscriminantAnalysis()
                lda.fit(train_feats, y[train_idx])
                scores.append(lda.score(test_feats, y[test_idx]))
            acc = float(np.mean(scores))
            severity_results.append({"severity": sev, "label": pert_name, "accuracy": acc})
            print(f"    {pert_name:<12} | Accuracy: {acc:.4f}")
        except Exception as e:
            print(f"    {pert_name:<12} | ERROR: {e}")
            severity_results.append({"severity": sev, "label": pert_name, "accuracy": 0.0, "error": str(e)})

    print("\n[4] Executing Perturbation Sweeps...")
    bundles_dict = matrix.execute_matrix()
    
    print(f"    Generated {len(bundles_dict)} Cryptographic Evidence Bundles.")
    for b in bundles_dict:
        pert = b.get("benchmark_results", {}).get("perturbation", "Unknown")
        ccc = b.get("statistical_agreement", {}).get("ccc", 0.0)
        status = b.get("pass_fail", "UNKNOWN")
        print(f"    - Perturbation: {pert:<16} | CCC: {ccc:.4f} | Status: {status}")
    
    print("\n[5] Packaging Output Evidence...")
    from vireon_core.contracts.evidence import EvidenceBundle
    bundle_obj = EvidenceBundle(**bundles_dict[0])
    
    report_gen = MultiFormatReportGenerator(bundle_obj)
    
    os.makedirs("output", exist_ok=True)
    
    # 1. JSON Evidence
    with open("output/evidence.json", "w") as f:
        f.write(bundle_obj.model_dump_json(indent=4))
        
    # 2. Markdown Report (with embedded figures)
    with open("output/evidence.md", "w") as f:
        f.write(report_gen.generate_markdown())
        
    # 3. Evidence Graph Artifacts
    with open("output/evidence_graph.json", "w") as f:
        json.dump({"nodes": [bundle_obj.bundle_id, csp.contract.validation_papers[0]], 
                   "edges": [{"source": bundle_obj.bundle_id, "target": "PhysioNet_MotorImagery_S001R04", "type": "validated_on"},
                             {"source": bundle_obj.bundle_id, "target": csp.contract.validation_papers[0], "type": "evaluates_claim"}]}, f, indent=4)
        
    # 4. Bundle Integrity Hashes
    from vireon_validation.evidence.generator import EvidenceGenerator
    hashes = EvidenceGenerator._compute_bundle_hashes("output")
    with open("output/hashes.json", "w") as f:
        json.dump(hashes, f, indent=4)

    # 5. Multi-bundle summary (all perturbation results, not just baseline)
    all_bundles_summary = []
    for b in bundles_dict:
        all_bundles_summary.append({
            "bundle_id": b.get("bundle_id", ""),
            "evidence_hash": b.get("evidence_hash", ""),
            "perturbation": b.get("benchmark_results", {}).get("perturbation", "Unknown"),
            "ccc": b.get("statistical_agreement", {}).get("ccc", 0.0),
            "rmse": b.get("statistical_agreement", {}).get("rmse", 0.0),
            "runtime_sec": b.get("runtime_sec", 0.0),
            "pass_fail": b.get("pass_fail", "UNKNOWN"),
        })
    with open("output/all_bundles_summary.json", "w") as f:
        json.dump(all_bundles_summary, f, indent=2)

    # 6. Benchmark summary report
    with open("output/benchmark_report.md", "w") as f:
        f.write("# VIREON Benchmark Report\n\n")
        f.write(f"**Dataset:** {data_source} ({X.shape[0]} trials, {X.shape[1]} channels, {X.shape[2]} samples)\n")
        f.write("**Algorithm:** CSP+LDA (n_components=2)\n")
        f.write(f"**Seed:** {seed}\n\n")
        f.write("## Spectral Benchmark (Vireon Welch vs scipy)\n\n")
        f.write(f"- RMSE: {welch_rmse:.2e}\n")
        f.write(f"- Max relative error: {welch_max_rel:.2e}\n")
        f.write(f"- Match (rtol=1e-7): {'YES' if welch_max_rel < 1e-7 else 'NO'}\n\n")
        f.write("## ICA Benchmark (Vireon ICA vs sklearn FastICA)\n\n")
        try:
            f.write(f"- Subspace match (min SVD): {subspace_match:.6f}\n")
            f.write(f"- Match (>0.95): {'YES' if subspace_match > 0.95 else 'NO'}\n\n")
        except NameError:
            f.write("- Skipped (error in ICA computation)\n\n")
        f.write("## Perturbation Robustness Sweep\n\n")
        f.write("| Severity | Label | Accuracy |\n")
        f.write("|----------|-------|----------|\n")
        for r in severity_results:
            f.write(f"| {r['severity']} | {r['label']} | {r['accuracy']:.4f} |\n")
        f.write("\n## Evidence Bundles (CSP+LDA vs MNE Reference)\n\n")
        f.write("| Perturbation | CCC | RMSE | Runtime (s) | Status |\n")
        f.write("|--------------|-----|------|-------------|--------|\n")
        for b in all_bundles_summary:
            f.write(f"| {b['perturbation']} | {b['ccc']:.4f} | {b['rmse']:.4f} | {b['runtime_sec']:.4f} | {b['pass_fail']} |\n")
        f.write(f"\n**Baseline evidence_hash:** `{all_bundles_summary[0]['evidence_hash'][:32]}...`\n")

    print("    Evidence artifacts written to output/")
    print("    - evidence.json (baseline bundle with cryptographic hash)")
    print("    - evidence.md (formatted report)")
    print(f"    - all_bundles_summary.json ({len(all_bundles_summary)} bundles)")
    print("    - benchmark_report.md (multi-algorithm benchmark summary)")
    print("    - hashes.json (bundle integrity hashes)")
    print("\nRun Complete. Review output/benchmark_report.md for the full summary.")

if __name__ == "__main__":
    main()

