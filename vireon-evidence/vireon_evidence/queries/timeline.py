from typing import List, Dict, Any
from vireon_evidence.graph.core import EvidenceGraph

class ScientificTimeline:
    """
    Tracks the historical progression of a method across time.
    """
    def __init__(self, graph: EvidenceGraph):
        self.graph = graph
        
    def generate_timeline(self, method_id: str) -> List[Dict[str, Any]]:
        """
        Extracts temporal progression of benchmarks, SRLs, and validation runs from the graph.
        """
        events = []
        bundles = self.graph.get_evidence_for_method(method_id)
        
        for b in bundles:
            meta = b.get("metadata", {})
            ts = meta.get("timestamp") or "2026-01-01"
            dataset = meta.get("dataset_id") or "Synthetic"
            status = b.get("status", "PASSED")
            ccc = meta.get("ccc") or b.get("icc")
            ccc_str = f" (CCC={ccc:.3f})" if ccc is not None else ""
            events.append({
                "date": str(ts),
                "event": f"Validation on {dataset} - Status: {status}{ccc_str}",
                "bundle_id": b.get("node_id"),
                "status": status
            })
            
        events.sort(key=lambda x: x["date"])
        return events
