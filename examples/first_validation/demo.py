import sys
import os
import json
import numpy as np

# Ensure vireon modules can be imported if running directly from repo root
sys.path.insert(0, os.path.abspath('../../vireon-core'))
sys.path.insert(0, os.path.abspath('../../vireon-models'))
sys.path.insert(0, os.path.abspath('../../vireon-methods'))
sys.path.insert(0, os.path.abspath('../../vireon-validation'))
sys.path.insert(0, os.path.abspath('../../vireon-evidence'))

from vireon_core.contracts.base import ISignal
from vireon_models.providers.datasets import SyntheticMotorImageryProvider
from vireon_methods.machine_learning.csp import CSPPlugin
from vireon_validation.benchmarks.matrix import BenchmarkMatrix
from vireon_validation.perturbations.library import WhiteNoisePerturbation, ChannelDropoutPerturbation, LineNoisePerturbation
from vireon_evidence.exporters.report_generator import MultiFormatReportGenerator

def main():
    print("==================================================")
    print("  VIREON - NATIVE NEUROSCIENCE EVIDENCE ENGINE    ")
    print("==================================================")
    
    print("\n[1] Synthesizing Deterministic Motor Imagery Dataset...")
    # This generates mathematically exact ERD/ERS phenomena matching real physiological models
    provider = SyntheticMotorImageryProvider(subject_id=1, seed=42)
    
    X_list, y_list = [], []
    for i in range(10):
        provider.trial_index = i
        provider._data = None
        data_dict = provider.get_data()
        X_list.append(data_dict["data"])
        y_list.append(data_dict["label"])
        
    X = np.array(X_list)
    X = np.transpose(X, (0, 2, 1)) # to (epochs, channels, times)
    y = np.array(y_list)
    y = (y % 2).astype(int) # Bin for CSP demo
    
    signal = ISignal(sampling_rate=data_dict["sample_rate"], data=X)
    labels = ISignal(sampling_rate=0, data=y)
    
    print(f"    Loaded {X.shape[0]} trials, {X.shape[1]} channels, {X.shape[2]} samples.")
    
    print("\n[2] Loading Algorithm Under Test (CSP)...")
    csp = CSPPlugin()
    print(f"    Purpose: {csp.contract.purpose}")
    print(f"    Assumptions: {', '.join(csp.contract.mathematical_assumptions)}")
    
    print("\n[3] Building Cartesian Benchmark Matrix...")
    matrix = BenchmarkMatrix()
    matrix.add_perturbation(WhiteNoisePerturbation(name="WhiteNoise", severity=0.5))
    matrix.add_perturbation(LineNoisePerturbation(severity=0.8, freq=60.0))
    matrix.add_perturbation(ChannelDropoutPerturbation(name="ChannelDropout", severity=0.2))
    
    print("\n[4] Executing Perturbation Sweeps...")
    csp.execute({"signal": signal, "labels": labels}) # Pre-fit for demo simplicity
    
    matrix.add_method(csp)
    matrix.add_dataset("SyntheticMotorImagery")
    bundles_dict = matrix.execute_matrix()
    
    print(f"    Generated {len(bundles_dict)} Cryptographic Evidence Bundles.")
    
    print("\n[5] Packaging Output Evidence...")
    # Render the reports
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
        json.dump({"nodes": [bundle_obj.bundle_id], "edges": [{"source": bundle_obj.bundle_id, "target": "SyntheticMotorImagery", "type": "validated_on"}]}, f, indent=4)
        
    print("    Evidence artifacts written to examples/first_validation/output/")
    print("\nRun Complete. You may now review output/evidence.md to see the generated figures and statistics.")

if __name__ == "__main__":
    main()
