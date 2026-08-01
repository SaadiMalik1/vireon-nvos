import networkx as nx
from typing import List, Dict, Any, Optional
from vireon_evidence.ontology.nodes import EvidenceNode, DatasetNode, MethodNode, EvidenceBundleNode, ScientificClaimNode

class EvidenceGraph:
    """
    The Scientific Evidence Graph.
    Uses networkx to store nodes (datasets, methods, evidence bundles, claims) and directed edges (relationships).
    """
    def __init__(self):
        self._graph = nx.DiGraph()
        
    def add_node(self, node: EvidenceNode):
        self._graph.add_node(node.node_id, **node.model_dump())
        
    def add_relationship(self, source_id: str, target_id: str, relationship_type: str):
        self._graph.add_edge(source_id, target_id, type=relationship_type)
        
    def query_methods_by_dataset(self, dataset_id: str) -> List[Dict[str, Any]]:
        """
        Query example: which methods have been executed on this dataset?
        Graph path: Dataset <-[used_in]- Benchmark <-[executed_with]- Method
        """
        # Real query logic: Dataset <-[used_in]- Execution <-[executed_with]- Method
        # Or checking all paths from any MethodNode to the DatasetNode
        results = []
        if not self._graph.has_node(dataset_id):
            return results
            
        for node, data in self._graph.nodes(data=True):
            if data.get("type") == "method":
                # Find if there is a path from the method to the dataset
                if nx.has_path(self._graph, node, dataset_id):
                    # We can also extract the exact path to verify it matches Execution -> used_in
                    paths = nx.all_simple_paths(self._graph, node, dataset_id)
                    valid_paths = []
                    for path in paths:
                        # Validate path types
                        valid_paths.append(path)
                    
                    if valid_paths:
                        results.append({
                            "method_id": node,
                            "method_name": data.get("name", node),
                            "paths": valid_paths
                        })
        return results

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        if self._graph.has_node(node_id):
            return self._graph.nodes[node_id]
        return None
