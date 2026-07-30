from typing import List, Dict, Set
from vireon_core.agency.causal_graph import CausalGraph, CausalStage, CausalNode

class AgencyValidator:
    """
    Validates agency integrity properties from a CausalGraph.
    """
    def __init__(self, causal_graph: CausalGraph):
        self.causal_graph = causal_graph
        self.nodes = causal_graph.get_nodes()

    def _get_nodes_by_stage(self, stage: CausalStage) -> List[CausalNode]:
        return [n for n in self.nodes if n.stage == stage]

    def _has_path(self, start_ids: Set[str], target_node: CausalNode) -> bool:
        if target_node.id in start_ids:
            return True
        for parent_id in target_node.parents:
            parent_node = next((n for n in self.nodes if n.id == parent_id), None)
            if parent_node and self._has_path(start_ids, parent_node):
                return True
        return False
        
    def _path_has_perturbation(self, target_node: CausalNode) -> bool:
        if target_node.is_perturbed:
            return True
        for parent_id in target_node.parents:
            parent_node = next((n for n in self.nodes if n.id == parent_id), None)
            if parent_node and self._path_has_perturbation(parent_node):
                return True
        return False

    def validate_false_activation(self) -> float:
        """
        Returns the rate of false activations. 
        A false activation is an ACTUATOR_STATE event without a valid causal path from an INTENTION event.
        """
        intentions = self._get_nodes_by_stage(CausalStage.INTENTION)
        actuators = self._get_nodes_by_stage(CausalStage.ACTUATOR_STATE)
        
        if not actuators:
            return 0.0
            
        intention_ids = {i.id for i in intentions}
        
        # If any actuator lacks a path back to ANY intention, it's a false activation
        false_activations = 0
        for act in actuators:
            if not intention_ids or not self._has_path(intention_ids, act):
                false_activations += 1
                
        return float(false_activations / len(actuators))

    def validate_command_substitution(self) -> float:
        """
        Returns the rate of command substitutions.
        Checks if the command executed diverges from the intent due to a causal perturbation.
        """
        actuators = self._get_nodes_by_stage(CausalStage.ACTUATOR_STATE)
        if not actuators:
            return 0.0
            
        substitutions = 0
        for act in actuators:
            if self._path_has_perturbation(act):
                substitutions += 1
                
        return float(substitutions / len(actuators))

    def compute_causal_latency(self) -> float:
        """
        Returns the time difference between INTENTION and ACTUATOR_STATE.
        """
        intentions = self._get_nodes_by_stage(CausalStage.INTENTION)
        actuators = self._get_nodes_by_stage(CausalStage.ACTUATOR_STATE)
        
        if intentions and actuators:
            return actuators[0].timestamp - intentions[0].timestamp
        return 0.0
        
    def generate_metrics(self) -> Dict[str, float]:
        return {
            "false_activation_rate": self.validate_false_activation(),
            "command_substitution_rate": self.validate_command_substitution(),
            "causal_propagation_latency": self.compute_causal_latency()
        }
