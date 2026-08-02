import numpy as np
from typing import List, Dict, Any, Optional
from vireon_evidence.graph.core import EvidenceGraph

class LeaderboardCategory:
    ACCURACY = "accuracy"
    FASTEST = "fastest"
    LOWEST_MEMORY = "lowest_memory"
    MOST_ROBUST = "most_robust"
    HIGHEST_SRL = "highest_srl"
    MOST_REPRODUCED = "most_reproduced"
    HIGHEST_CONFIDENCE = "highest_confidence"
    MOST_PUBLICATIONS = "most_publications"

class ScientificLeaderboard:
    def __init__(self, graph: EvidenceGraph):
        self.graph = graph
        
    def generate(self, category: str = LeaderboardCategory.HIGHEST_CONFIDENCE, method_type: Optional[str] = "CSP") -> List[Dict[str, Any]]:
        """
        Ranks methods of a certain type based on the specified category using graph aggregations.
        """
        methods = self.graph.get_methods(method_type=method_type)
        if not methods and method_type is not None:
            # Fallback to all methods if no filter matches
            methods = self.graph.get_methods(method_type=None)
            
        ranked = []
        for m in methods:
            m_id = m["node_id"]
            m_name = m.get("canonical_name", m_id)
            meta = m.get("metadata", {})
            bundles = self.graph.get_evidence_for_method(m_id)
            
            # Aggregate metrics
            cccs = [b.get("metadata", {}).get("ccc") or b.get("icc") for b in bundles if (b.get("metadata", {}).get("ccc") is not None or b.get("icc") is not None)]
            rmses = [b.get("rmse") for b in bundles if b.get("rmse") is not None]
            exec_times = [b.get("metadata", {}).get("execution_time_ms") for b in bundles if b.get("metadata", {}).get("execution_time_ms") is not None]
            
            avg_ccc = float(np.mean(cccs)) if cccs else 0.0
            avg_rmse = float(np.mean(rmses)) if rmses else float("inf")
            avg_time = float(np.mean(exec_times)) if exec_times else float("inf")
            srl = meta.get("srl", "SRL-0")
            
            info = {
                "method": m_name,
                "method_id": m_id,
                "srl": srl,
                "ccc": avg_ccc,
                "rmse": avg_rmse,
                "reproductions": len(bundles),
                "execution_time_ms": avg_time,
                "n_bundles": len(bundles)
            }
            ranked.append(info)
            
        # Sort based on category
        if category == LeaderboardCategory.HIGHEST_CONFIDENCE or category == LeaderboardCategory.ACCURACY:
            ranked.sort(key=lambda x: x["ccc"], reverse=True)
        elif category == LeaderboardCategory.FASTEST:
            ranked.sort(key=lambda x: x["execution_time_ms"])
        elif category == LeaderboardCategory.MOST_REPRODUCED:
            ranked.sort(key=lambda x: x["reproductions"], reverse=True)
        elif category == LeaderboardCategory.HIGHEST_SRL:
            ranked.sort(key=lambda x: x["srl"], reverse=True)
        else:
            ranked.sort(key=lambda x: x["ccc"], reverse=True)
            
        for rank_idx, item in enumerate(ranked, start=1):
            item["rank"] = rank_idx
            
        return ranked
