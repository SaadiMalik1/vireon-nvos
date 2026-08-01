import os
import json
import ast
from typing import Dict, Any, List, Optional
import networkx as nx

class KnowledgeGraph:
    """
    A lightweight inference engine that parses the JSON-LD scientific knowledge graph
    to evaluate hypotheses and generate evidence-backed recommendations.
    """
    def __init__(self, knowledge_root: str):
        self.knowledge_root = knowledge_root
        self.graph = nx.DiGraph()
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
                    self.load_from_jsonld(path)

    def load_from_jsonld(self, filepath: str):
        """Parse JSON-LD, add nodes and edges to graph."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                
            # Basic JSON-LD parsing to populate graph and index
            if "rules" in data:
                for rule in data["rules"]:
                    node_id = rule["@id"]
                    self.graph.add_node(node_id, **rule)
                    self.index[node_id] = rule
                    
                    target = rule.get("target_method")
                    if target:
                        self.graph.add_edge(target, node_id, relationship="HAS_RULE")
                        
            if "methods" in data:
                for method_name, method_info in data["methods"].items():
                    node_id = method_info["@id"]
                    self.graph.add_node(node_id, **method_info)
                    self.index[node_id] = method_info
                    
                    for assumption in method_info.get("assumptions", []):
                        self.graph.add_edge(node_id, assumption, relationship="REQUIRES")

            if "assumptions" in data:
                # assumptions.jsonld might have {"assumptions": {"Stationarity": {"@id": ...}}}
                if isinstance(data["assumptions"], dict):
                    for a_name, a_info in data["assumptions"].items():
                        node_id = a_info["@id"]
                        self.graph.add_node(node_id, **a_info)
                        self.index[node_id] = a_info
                elif isinstance(data["assumptions"], list):
                    for a_info in data["assumptions"]:
                        node_id = a_info["@id"]
                        self.graph.add_node(node_id, **a_info)
                        self.index[node_id] = a_info
                        
        except json.JSONDecodeError:
            print(f"Warning: Failed to parse {filepath}")

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        return self.index.get(node_id)
        
    def _evaluate_condition(self, condition_str: str, context: Dict[str, Any]) -> bool:
        """Safely evaluates a condition string against the provided context dictionary."""
        try:
            tree = ast.parse(condition_str, mode='eval')
            
            # Very restricted visitor that only allows specific operations
            class Evaluator(ast.NodeVisitor):
                def visit_Expression(self, node):
                    return self.visit(node.body)
                    
                def visit_Compare(self, node):
                    left = self.visit(node.left)
                    right = self.visit(node.comparators[0])
                    op = type(node.ops[0])
                    
                    if op == ast.Eq:
                        return left == right
                    elif op == ast.NotEq:
                        return left != right
                    elif op == ast.Lt:
                        return left < right
                    elif op == ast.LtE:
                        return left <= right
                    elif op == ast.Gt:
                        return left > right
                    elif op == ast.GtE:
                        return left >= right
                    raise ValueError(f"Unsupported operator: {op}")
                    
                def visit_Attribute(self, node):
                    # Handle cases like signal.stationarity by treating them as a single string key
                    val = self.visit(node.value)
                    return context.get(f"{val}.{node.attr}")
                    
                def visit_Name(self, node):
                    if node.id in ['True', 'False', 'None']:
                        return {'True': True, 'False': False, 'None': None}[node.id]
                    if node.id in context:
                        return context[node.id]
                    return node.id
                    
                def visit_Constant(self, node):
                    return node.value
            
            return Evaluator().visit(tree)
        except Exception as e:
            print(f"Failed to evaluate condition '{condition_str}': {e}")
            return False

    def validate_methodology(self, method_id: str, observed: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Walk the graph from method -> assumptions -> rules, evaluate each.
        Returns a list of violations.
        """
        if method_id not in self.graph:
            # Fallback search if a short ID is passed (e.g. "Welch" instead of "vk:Method:Welch")
            possible_matches = [n for n in self.graph.nodes() if str(n).endswith(method_id)]
            if possible_matches:
                method_id = possible_matches[0]
            else:
                return []
                
        violations = []
        
        # Check rules connected directly to the method
        for u, v, data in self.graph.edges(method_id, data=True):
            if data.get('relationship') == 'HAS_RULE':
                rule_node = self.graph.nodes[v]
                condition = rule_node.get("condition")
                
                # if condition is FALSE, it's a violation
                # The rule condition is "signal.stationarity == True".
                # If we have {"signal.stationarity": False}, the condition returns False -> violation.
                if condition and not self._evaluate_condition(condition, observed):
                    violations.append({
                        "rule": v,
                        "description": rule_node.get("message"),
                        "severity": rule_node.get("violation_severity"),
                        "recommendation": rule_node.get("recommendation")
                    })
                    
        return violations
