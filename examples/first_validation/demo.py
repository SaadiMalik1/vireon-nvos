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
from vireon_models.providers.datasets import PhysioNetMotorImageryProvider
from vireon_methods.machine_learning.csp import CSPPlugin
from vireon_validation.benchmarks.matrix import BenchmarkMatrix
from vireon_validation.perturbations.library import WhiteNoisePerturbation, ChannelDropoutPerturbation, LineNoisePerturbation
from vireon_evidence.exporters.report_generator import MultiFormatReportGenerator

def main():
    print("==================================================")
    print("  VIREON - NATIVE NEUROSCIENCE EVIDENCE ENGINE    ")
    print("==================================================")
    
    print("\n[1] Loading REAL PhysioNet Motor Imagery Dataset...")
    # This loads the actual biological dataset from ~/mne_data
    provider = PhysioNetMotorImageryProvider(subject_id=1, run_id=4)
    data_dict = provider.get_data()
    
    X = data_dict["data"] # shape is already (epochs, channels, times) from MNE
    y = data_dict["label"]
    
    signal = ISignal(sampling_rate=data_dict["sample_rate"], data=X)
    labels = ISignal(sampling_rate=0, data=y)
    
    print(f"    Loaded {X.shape[0]} trials, {X.shape[1]} channels, {X.shape[2]} samples.")
    
    print("\n[2] Loading Algorithm Under Test (CSP)...")
    csp = CSPPlugin()
    print(f"    Purpose: {csp.contract.purpose}")
    print(f"    Assumptions: {', '.join(csp.contract.mathematical_assumptions)}")
    print(f"    Validation Papers: {', '.join(csp.contract.validation_papers)}")
    
    print("\n[3] Building Cartesian Benchmark Matrix...")
    matrix = BenchmarkMatrix()
    matrix.add_perturbation(WhiteNoisePerturbation(name="WhiteNoise", severity=0.5))
    matrix.add_perturbation(LineNoisePerturbation(severity=0.8, freq=60.0))
    matrix.add_perturbation(ChannelDropoutPerturbation(name="ChannelDropout", severity=0.2))
    
    print("\n[4] Executing Perturbation Sweeps...")
    # Pre-fit for demo simplicity to ensure no dimensionality issues
    csp.execute({"signal": signal, "labels": labels}) 
    
    matrix.add_method(csp)
    matrix.add_dataset("PhysioNet_MotorImagery_S001R04")
    bundles_dict = matrix.execute_matrix()
    
    print(f"    Generated {len(bundles_dict)} Cryptographic Evidence Bundles.")
    
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
        
    print("    Evidence artifacts written to examples/first_validation/output/")
    print("\nRun Complete. You may now review output/evidence.md to see the generated figures and statistics.")

if __name__ == "__main__":
    main()
