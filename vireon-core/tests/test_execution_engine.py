import sys
import os
# Adjust path for testing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from vireon_lab.scenarios.schema import load_scenario_from_yaml
from vireon_core.kernel.execution_engine import ExecutionEngine
from vireon_validation.evidence.generator import EvidenceGenerator

def test_pipeline():
    scenario_path = os.path.join(os.path.dirname(__file__), '..', '..', 'vireon-lab', 'vireon_lab', 'scenarios', 'mock_scenario.yaml')
    
    # Load Scenario
    scenario = load_scenario_from_yaml(scenario_path)
    print(f"Loaded scenario: {scenario.schema.id}")

    # Initialize Engine
    evidence = ExecutionEngine.run(scenario)
    
    # Execute and get evidence
    print(f"Executed scenario, got execution hash: {evidence.execution_hash}")
    print(f"Captured {len(evidence.events)} events and {len(evidence.measurements)} measurements.")

    gen = EvidenceGenerator(evidence, os.path.join(os.path.dirname(__file__), "..", "evidence_output"))
    gen.generate_bundle()

if __name__ == "__main__":
    test_pipeline()
