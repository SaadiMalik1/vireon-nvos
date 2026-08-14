import numpy as np
from typing import Dict, Any
from vireon_evidence.graph.core import EvidenceGraph

class EvidenceService:
    """
    Core service layer for querying the Evidence Graph.
    Decoupled from presentation (CLI, API, Web).
    """
    def __init__(self, graph: EvidenceGraph):
        self.graph = graph
        
    def get_method_profile(self, method_name: str) -> Dict[str, Any]:
        """
        Retrieves a living scientific profile for a method from the Evidence Graph.
        """
        bundles = self.graph.get_evidence_for_method(method_name)
        
        node = self.graph.get_node(method_name)
        meta = node.get("metadata", {}) if node else {}
        
        cccs = [b.get("metadata", {}).get("ccc") or b.get("icc") for b in bundles if (b.get("metadata", {}).get("ccc") is not None or b.get("icc") is not None)]
        rmses = [b.get("rmse") for b in bundles if b.get("rmse") is not None]
        exec_times = [b.get("metadata", {}).get("execution_time_ms") for b in bundles if b.get("metadata", {}).get("execution_time_ms") is not None]
        
        datasets = list(set([b.get("metadata", {}).get("dataset_id") for b in bundles if b.get("metadata", {}).get("dataset_id")]))
        
        failures = [b.get("node_id") for b in bundles if b.get("status") == "FAILED"]
        
        # Check publications linked to method
        publications = []
        if self.graph._graph.has_node(method_name):
            for neighbor in self.graph._graph.successors(method_name):
                n_data = self.graph._graph.nodes[neighbor]
                if n_data.get("node_type") == "Publication":
                    publications.append(n_data.get("doi", neighbor))
                    
        return {
            "method": method_name,
            "total_benchmarks": len(bundles),
            "datasets": datasets,
            "metrics": {
                "rmse": float(np.mean(rmses)) if rmses else None,
                "ccc": float(np.mean(cccs)) if cccs else None,
                "execution_time_ms": float(np.mean(exec_times)) if exec_times else None,
            },
            "current_srl": meta.get("srl", "SRL-0"),
            "failure_cases": failures,
            "publications": publications
        }
