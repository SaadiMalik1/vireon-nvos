import numpy as np
from typing import Dict, Any, List
from vireon_evidence.graph.core import EvidenceGraph

class ContinuousMetaAnalysis:
    """
    Continuously recomputes overall confidence, effect size, heterogeneity, 
    publication bias indicators, and recommended SRL using random-effects meta-analysis.
    """
    def __init__(self, graph: EvidenceGraph):
        self.graph = graph
        
    def _recommend_srl(self, pooled_effect: float, n_studies: int) -> str:
        if n_studies >= 4 and pooled_effect >= 0.99:
            return "SRL-6"
        elif n_studies >= 2 and pooled_effect >= 0.95:
            return "SRL-4"
        elif n_studies >= 1 and pooled_effect >= 0.90:
            return "SRL-3"
        elif pooled_effect >= 0.80:
            return "SRL-2"
        elif pooled_effect > 0.0:
            return "SRL-1"
        return "SRL-0"
        
    def recompute(self, method_id: str) -> Dict[str, Any]:
        """
        Executed after every new benchmark for a method.
        Performs DerSimonian-Laird random-effects meta-analysis over evidence bundles.
        """
        bundles = self.graph.get_evidence_for_method(method_id)
        if not bundles:
            return {
                "method_id": method_id,
                "overall_confidence": 0.0,
                "effect_size": 0.0,
                "confidence_interval": [0.0, 0.0],
                "heterogeneity_i2": 0.0,
                "n_studies": 0,
                "recommended_srl": "SRL-0"
            }
            
        effect_sizes = []
        variances = []
        for b in bundles:
            meta = b.get("metadata", {})
            val = meta.get("ccc") if meta.get("ccc") is not None else b.get("icc")
            if val is not None:
                effect_sizes.append(float(val))
                # Variance: use recorded variance or standard error estimate
                var = meta.get("variance") or 0.001
                variances.append(float(var))
                
        if not effect_sizes:
            return {
                "method_id": method_id,
                "overall_confidence": 0.0,
                "effect_size": 0.0,
                "confidence_interval": [0.0, 0.0],
                "heterogeneity_i2": 0.0,
                "n_studies": 0,
                "recommended_srl": "SRL-0"
            }
            
        y = np.array(effect_sizes)
        v = np.array(variances)
        
        # Fixed effects weights
        w = 1.0 / np.maximum(v, 1e-6)
        w_sum = np.sum(w)
        fixed_effect = np.sum(w * y) / w_sum
        
        # Cochran's Q for heterogeneity
        k = len(y)
        if k > 1:
            q = np.sum(w * (y - fixed_effect) ** 2)
            df = k - 1
            # DerSimonian-Laird tau^2
            c = w_sum - np.sum(w ** 2) / w_sum
            tau2 = max(0.0, (q - df) / c) if c > 0 else 0.0
            # Heterogeneity I^2
            i2 = max(0.0, float((q - df) / q * 100.0)) if q > 0 else 0.0
            # Random effects weights
            w_rand = 1.0 / (v + tau2)
            pooled_effect = float(np.sum(w_rand * y) / np.sum(w_rand))
            se = float(np.sqrt(1.0 / np.sum(w_rand)))
        else:
            i2 = 0.0
            pooled_effect = float(y[0])
            se = float(np.sqrt(v[0]))
            
        ci_lower = max(0.0, pooled_effect - 1.96 * se)
        ci_upper = min(1.0, pooled_effect + 1.96 * se)
        
        return {
            "method_id": method_id,
            "overall_confidence": pooled_effect,
            "effect_size": pooled_effect,
            "confidence_interval": [ci_lower, ci_upper],
            "heterogeneity_i2": i2,
            "n_studies": k,
            "recommended_srl": self._recommend_srl(pooled_effect, k)
        }
