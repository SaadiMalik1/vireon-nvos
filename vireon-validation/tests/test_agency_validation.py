import sys
import os
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from vireon_core.agency.causal_graph import CausalGraph, CausalStage
from vireon_validation.agency import AgencyValidator

class TestAgencyValidation(unittest.TestCase):
    def test_false_activation_none_intent(self):
        graph = CausalGraph()
        n1 = graph.add_node(CausalStage.INTENTION, "Intention: normal")
        n2 = graph.add_node(CausalStage.ACTUATOR_STATE, "Command executed: jump")
        # No parents linking n2 to n1
        
        validator = AgencyValidator(graph)
        metrics = validator.generate_metrics()
        self.assertEqual(metrics["false_activation_rate"], 1.0)
        self.assertEqual(metrics["command_substitution_rate"], 0.0)

    def test_command_substitution(self):
        graph = CausalGraph()
        n1 = graph.add_node(CausalStage.INTENTION, "Intention")
        n_pert = graph.add_node(CausalStage.SIGNAL, "Perturbation", parents=[n1], is_perturbed=True)
        n2 = graph.add_node(CausalStage.COMMAND, "Command", parents=[n_pert])
        n3 = graph.add_node(CausalStage.ACTUATOR_STATE, "Action", parents=[n2])
        
        validator = AgencyValidator(graph)
        metrics = validator.generate_metrics()
        self.assertEqual(metrics["command_substitution_rate"], 1.0)
        
    def test_no_violation(self):
        graph = CausalGraph()
        n1 = graph.add_node(CausalStage.INTENTION, "Intention")
        n2 = graph.add_node(CausalStage.COMMAND, "Command", parents=[n1])
        n3 = graph.add_node(CausalStage.ACTUATOR_STATE, "Action", parents=[n2])
        
        validator = AgencyValidator(graph)
        metrics = validator.generate_metrics()
        self.assertEqual(metrics["false_activation_rate"], 0.0)
        self.assertEqual(metrics["command_substitution_rate"], 0.0)

if __name__ == "__main__":
    unittest.main()
