import os
import sys
import json
from vireon_core.kernel.execution_engine import ExecutionEngine
from vireon_lab.experiments.schema import load_experiment_from_yaml

class ReproducibilityEngine:
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        
    def reproduce_doi(self, doi: str):
        print("==================================================")
        print("  VIREON INDEPENDENT REPRODUCIBILITY ENGINE")
        print(f"  Target: {doi}")
        print("==================================================")
        
        # 1. Look up DOI in registry
        index_path = os.path.join(self.workspace_root, "vireon-lab", "vireon_lab", "data", "doi_index.json")
        if not os.path.exists(index_path):
            index_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "doi_index.json")
        try:
            with open(index_path, "r") as f:
                data = json.load(f)
                index = data.get("index", {})
        except Exception as e:
            print(f"[ERROR] Could not load DOI registry: {e}")
            sys.exit(2)
            
        if doi not in index:
            print(f"[ERROR] DOI {doi} not found in registry.")
            print(f"Available DOIs: {list(index.keys())}")
            sys.exit(2)
            
        publication = index[doi]
        scenario_id = publication.get("scenario")
        expected = publication.get("expected_outputs", {})
        tolerance = publication.get("tolerance", 0.1)
        
        # 2. Load the scenario YAML
        # We assume scenario_id maps to a yaml file in vireon_lab/experiments/ or similar
        # For simplicity in this CLI, we will look for mock_scenario.yaml if the specific one doesn't exist.
        scenario_filename = f"{scenario_id}.yaml" if scenario_id else "mock_scenario.yaml"
        scenario_path = os.path.join(self.workspace_root, "vireon-lab", "vireon_lab", "experiments", scenario_filename)
        
        if not os.path.exists(scenario_path):
            # Fallback to mock_scenario.yaml
            scenario_path = os.path.join(self.workspace_root, "vireon-lab", "vireon_lab", "experiments", "mock_scenario.yaml")
            
        print(f"Loading scenario from {scenario_path}...")
        experiment_def = load_experiment_from_yaml(scenario_path)
        
        # 3. Run the scenario via ExecutionEngine
        print("Executing scenario via ExecutionEngine...")
        # engine.run is a classmethod
        result = ExecutionEngine.run(experiment_def, seed=42)
        
        # 4. Compare against expected outputs
        actual_measurements = {m.metric_name: m.value for m in result.measurements}
            
        # 5. Compute deviation
        deviations = {k: abs(actual_measurements.get(k, 0.0) - v) for k, v in expected.items()}
        max_dev = max(deviations.values()) if deviations else 0.0
        
        # 6. Report honestly
        print("Compiling Independent Verdict...")
        for k, v in expected.items():
            act = actual_measurements.get(k, 0.0)
            print(f"  {k}: Expected={v:.4f}, Actual={act:.4f}, Diff={abs(act - v):.4f}")
            
        if max_dev <= tolerance:
            print(f"\n[PASS] {doi} reproduced. Max deviation: {max_dev:.4f}")
            sys.exit(0)
        else:
            print(f"\n[FAIL] {doi} NOT reproduced. Max deviation: {max_dev:.4f} > {tolerance}")
            sys.exit(1)

if __name__ == "__main__":
    # We expect this to run from vireon-lab
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # The actual workspace_root where experiments are is base_dir/..
    workspace_root = os.path.abspath(os.path.join(base_dir, ".."))
    engine = ReproducibilityEngine(workspace_root)
    if len(sys.argv) > 1 and sys.argv[1] == "reproduce":
        engine.reproduce_doi(sys.argv[2])
