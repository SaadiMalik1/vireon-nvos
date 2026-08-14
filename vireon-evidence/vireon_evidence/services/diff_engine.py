from vireon_core.contracts.evidence import EvidenceBundle
from typing import Dict, Any

class EvidenceDiffEngine:
    """
    Computes structural and numerical differences between two EvidenceBundles.
    """
    @staticmethod
    def diff(bundle_a: EvidenceBundle, bundle_b: EvidenceBundle) -> Dict[str, Any]:
        """
        Returns a diff dictionary comparing metrics, assumptions, runtime, and conclusions.
        """
        diff_report = {}
        
        # 1. Compare Conclusions
        if bundle_a.conclusion_verdict != bundle_b.conclusion_verdict:
            diff_report["conclusions"] = {
                "bundle_a": bundle_a.conclusion_verdict,
                "bundle_b": bundle_b.conclusion_verdict
            }
            
        # 2. Compare Metrics
        metric_diffs = {}
        for key in bundle_a.statistical_agreement:
            val_a = bundle_a.statistical_agreement.get(key)
            val_b = bundle_b.statistical_agreement.get(key)
            if val_a != val_b:
                metric_diffs[key] = {"a": val_a, "b": val_b, "delta": (val_b or 0) - (val_a or 0)}
        if metric_diffs:
            diff_report["metrics"] = metric_diffs
            
        return diff_report
