import sys
import os
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from vireon_core.agency.causal_graph import CausalGraph, CausalStage
from vireon_core.kernel.execution_engine import ExecutionEngine
from vireon_lab.scenarios.schema import load_scenario_from_yaml
import tempfile
import yaml

class TestCausalGraph(unittest.TestCase):
    def test_causal_graph_construction(self):
        graph = CausalGraph()
        n1 = graph.add_node(CausalStage.INTENTION, "Intention established")
        n2 = graph.add_node(CausalStage.NEURAL_STATE, "State captured", parents=[n1])
        
        nodes = graph.get_nodes()
        self.assertEqual(len(nodes), 2)
        
        n2_node = next(n for n in nodes if n.id == n2)
        self.assertEqual(n2_node.parents, [n1])
        
    def test_execution_engine_causal_trace(self):
        yaml_content = {
            "id": "test.agency",
            "classification": {"type": "agency_integrity", "threat_level": "L2"},
            "system": {"provider": "mock"},
            "stimulus": {"intended_action": "none"},
            "expected": {"actuator_command": "none"},
            "measurements": ["false_activation"],
            "evidence": ["event_trace"]
        }
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(yaml_content, f)
            temp_path = f.name
            
        try:
            scenario = load_scenario_from_yaml(temp_path)
            evidence = ExecutionEngine.run(scenario)
                        
            # Verify events match causal stages
            stages_found = [e.causal_stage for e in evidence.events]
            self.assertIn(CausalStage.INTENTION.value, stages_found)
            self.assertIn(CausalStage.FEEDBACK.value, stages_found)
            self.assertTrue(len(evidence.events) >= 6) # At least intention, neural, signal, decoder, command, actuator, feedback
            
        finally:
            os.remove(temp_path)

if __name__ == "__main__":
    unittest.main()
