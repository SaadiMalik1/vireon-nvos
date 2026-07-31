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
        # Simplified query logic for stub
        results = []
        for u, v, data in self._graph.edges(data=True):
            if v == dataset_id and data.get("type") == "used_in":
                # u is Benchmark or Bundle
                pass
        return results

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        if self._graph.has_node(node_id):
            return self._graph.nodes[node_id]
        return None
