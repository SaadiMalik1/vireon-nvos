import os
import json
from typing import Dict, Any, List, Optional

class KnowledgeGraph:
    """
    A lightweight inference engine that parses the JSON-LD scientific knowledge graph
    to evaluate hypotheses and generate evidence-backed recommendations.
    """
    def __init__(self, knowledge_root: str):
        self.knowledge_root = knowledge_root
        self.graph: Dict[str, Any] = {}
        self.index: Dict[str, Any] = {}
        self._load_graph()

    def _load_graph(self):
        """Recursively loads all .jsonld files in the knowledge root into a unified graph."""
        if not os.path.exists(self.knowledge_root):
            return
            
        for root, _, files in os.walk(self.knowledge_root):
            for file in files:
                if file.endswith('.jsonld'):
                    path = os.path.join(root, file)
                    try:
                        with open(path, 'r') as f:
                            data = json.load(f)
                            self._index_nodes(data)
                    except json.JSONDecodeError:
                        print(f"Warning: Failed to parse {path}")

    def _index_nodes(self, data: Any):
        """Indexes JSON-LD nodes by @id for fast traversal."""
        if isinstance(data, dict):
            if "@id" in data:
                self.index[data["@id"]] = data
            for key, value in data.items():
                self._index_nodes(value)
        elif isinstance(data, list):
            for item in data:
                self._index_nodes(item)

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        return self.index.get(node_id)
        
    def evaluate_methodology(self, method_id: str, observed_properties: Dict[str, bool]) -> Dict[str, Any]:
        """
        Evaluates a methodology against observed signal properties.
        Execution flow: Scientific Fact -> Relationship -> Evidence -> Recommendation
        """
        method_node = self.get_node(method_id)
        if not method_node:
            return {"status": "UNKNOWN", "message": f"Method {method_id} not found in knowledge graph."}
            
        required_assumptions = method_node.get("requires_assumptions", [])
        
        violations = []
        for assumption_id in required_assumptions:
            assumption_node = self.get_node(assumption_id)
            if not assumption_node:
                continue
                
            property_key = assumption_node.get("property_key")
            expected_value = assumption_node.get("expected_value")
            
            if property_key in observed_properties:
                if observed_properties[property_key] != expected_value:
                    violations.append({
                        "assumption": assumption_id,
                        "description": assumption_node.get("description"),
                        "evidence": f"Observed {property_key}={observed_properties[property_key]}, expected {expected_value}",
                        "recommendation": assumption_node.get("fallback_recommendation", "Consider an alternative method.")
                    })
                    
        if violations:
            return {
                "status": "VIOLATED",
                "confidence": 0.9,
                "violations": violations,
                "recommendation": violations[0]["recommendation"]
            }
            
        return {
            "status": "SATISFIED",
            "confidence": 1.0,
            "message": "All required assumptions are satisfied by the observed properties."
        }
