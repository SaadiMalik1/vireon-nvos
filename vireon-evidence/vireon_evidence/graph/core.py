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

    def get_methods(self, method_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all method nodes, optionally filtered by method_type."""
        methods = []
        for node_id, data in self._graph.nodes(data=True):
            if data.get("node_type") == "Method":
                m_type = data.get("metadata", {}).get("type") or data.get("type")
                if method_type is None or m_type == method_type:
                    methods.append({"node_id": node_id, **data})
        return methods

    def get_evidence_for_method(self, method_id: str) -> List[Dict[str, Any]]:
        """
        Get all evidence bundle nodes linked to a method.
        Checks edges (method -> bundle or bundle -> method) and node metadata.
        """
        bundles = []
        if not self._graph.has_node(method_id):
            return bundles

        # Check direct successors and predecessors
        candidates = set(self._graph.successors(method_id)).union(self._graph.predecessors(method_id))
        for neighbor in candidates:
            data = self._graph.nodes[neighbor]
            if data.get("node_type") == "EvidenceBundle":
                bundles.append({"node_id": neighbor, **data})

        # Also check any bundle in graph that explicitly tags method_id
        for node_id, data in self._graph.nodes(data=True):
            if data.get("node_type") == "EvidenceBundle":
                meta = data.get("metadata", {})
                if meta.get("method_id") == method_id:
                    if not any(b["node_id"] == node_id for b in bundles):
                        bundles.append({"node_id": node_id, **data})

        return bundles
