from typing import List, Dict, Any
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
        
    def generate(self, category: str, method_type: str = "CSP") -> List[Dict[str, Any]]:
        """
        Ranks methods of a certain type based on the specified category using graph aggregations.
        """
        # Stub logic
        if category == LeaderboardCategory.HIGHEST_CONFIDENCE:
            return [
                {"rank": 1, "method": "MNE", "srl": "SRL-6", "ccc": 0.998, "rmse": 1e-6},
                {"rank": 2, "method": "VIREON CSP", "srl": "SRL-3", "ccc": 0.992, "rmse": 1.2e-6},
                {"rank": 3, "method": "Experimental Bayesian CSP", "srl": "SRL-2", "ccc": 0.98, "rmse": 2e-6}
            ]
        elif category == LeaderboardCategory.MOST_REPRODUCED:
            return [
                {"rank": 1, "method": "SciPy Welch", "reproductions": 128},
                {"rank": 2, "method": "MNE Welch", "reproductions": 45}
            ]
        
        return []
