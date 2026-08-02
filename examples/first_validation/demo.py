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

from vireon_core.contracts.base import ISignal
from vireon_core.runtime.rng import DeterministicRNG
from vireon_models.providers.datasets import PhysioNetMotorImageryProvider
from vireon_methods.machine_learning.csp import CSPPlugin
from vireon_validation.benchmarks.matrix import BenchmarkMatrix
from vireon_validation.perturbations.library import WhiteNoisePerturbation, ChannelDropoutPerturbation, LineNoisePerturbation
from vireon_evidence.exporters.report_generator import MultiFormatReportGenerator

def _generate_pink_noise(n: int, rng: DeterministicRNG) -> np.ndarray:
    """Generate 1/f pink noise using spectral method."""
    freqs = np.fft.rfftfreq(n)
    freqs[0] = 1.0  # avoid div by zero
    spectrum = rng.normal(0.0, 1.0, len(freqs)) / np.sqrt(freqs)
    spectrum[0] = 0.0
    noise = np.fft.irfft(spectrum, n=n)
    return noise / (np.std(noise) + 1e-10)  # normalize

def _generate_synthetic_motor_imagery(seed: int = 42, n_epochs: int = 40, n_channels: int = 8, 
                                      n_samples: int = 250, fs: float = 250.0):
    """Generate synthetic motor imagery data with a real ERD/ERS pattern.
    
    Class 0 (left hand): high mu-band (8-12 Hz) power in central channels.
    Class 1 (right hand): low mu-band power (ERD) in central channels.
    
    This ensures CSP can find a discriminative spatial filter.
    """
    rng = DeterministicRNG(seed)
    
    X = np.zeros((n_epochs, n_channels, n_samples))
    y = np.array([0, 1] * (n_epochs // 2))
    
    t = np.arange(n_samples) / fs
    mu_freq = 10.0  # Hz
    
    for i in range(n_epochs):
        # Background 1/f noise
        for ch in range(n_channels):
            X[i, ch] = _generate_pink_noise(n_samples, rng) * 0.5
        
        if y[i] == 0:
            # Class 0: high mu power (ERS) — stronger in central channels
            mu_power = 8.0  # µV
            for ch in range(n_channels):
                if ch in (2, 3, 4, 5):  # central channels
                    X[i, ch] += mu_power * np.sin(2 * np.pi * mu_freq * t)
                else:
                    X[i, ch] += 2.0 * np.sin(2 * np.pi * mu_freq * t)
        else:
            # Class 1: low mu power (ERD) — weaker everywhere
            mu_power = 1.5  # µV
            for ch in range(n_channels):
                X[i, ch] += mu_power * np.sin(2 * np.pi * mu_freq * t)
    
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
    matrix.add_perturbation(WhiteNoisePerturbation(name="WhiteNoise", severity=0.5))
    matrix.add_perturbation(LineNoisePerturbation(severity=0.8, freq=60.0))
    matrix.add_perturbation(ChannelDropoutPerturbation(name="ChannelDropout", severity=0.2))
    
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
        
    print("    Evidence artifacts written to output/")
    print("\nRun Complete. You may now review output/evidence.md to see the generated figures and statistics.")

if __name__ == "__main__":
    main()

