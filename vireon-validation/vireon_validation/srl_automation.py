from typing import List, Dict, Any
from vireon_core.contracts.evidence import EvidenceBundle

class SRLAutomator:
    @staticmethod
    def recommend_srl(evidence_bundles: List[EvidenceBundle]) -> Dict[str, Any]:
        """
        Recommends a Scientific Readiness Level (SRL) based on meta-analysis
        of accumulated EvidenceBundles.
        """
        if not evidence_bundles:
            return {"recommended_srl": "SRL-1", "reason": ["No evidence bundles available."]}
            
        successful_reproductions = sum(1 for eb in evidence_bundles if eb.conclusion_verdict == "PASS")
        total_runs = len(evidence_bundles)
        
        # Determine datasets coverage
        datasets_used = set(eb.dataset_provenance.dataset_id for eb in evidence_bundles)
        
        # Compute mean ICC or CCC if available
        ccc_values = [eb.statistical_agreement.get("ccc", 0.0) for eb in evidence_bundles if "ccc" in eb.statistical_agreement]
        mean_ccc = sum(ccc_values) / len(ccc_values) if ccc_values else 0.0
        
        reasons = []
        recommended_srl = "SRL-1"
        
        reasons.append(f"{successful_reproductions} successful reproductions out of {total_runs}")
        reasons.append(f"Reproduced on {len(datasets_used)} distinct datasets")
        
        if successful_reproductions > 10 and len(datasets_used) >= 3 and mean_ccc > 0.94999:
            recommended_srl = "SRL-4"
            reasons.append("Mean CCC > 0.95 across multiple datasets.")
        elif successful_reproductions > 5 and len(datasets_used) >= 1:
            recommended_srl = "SRL-3"
            reasons.append("Evidence across real datasets collected.")
        elif successful_reproductions > 0:
            recommended_srl = "SRL-2"
            reasons.append("Initial synthetic benchmarking passed.")
            
        return {
            "recommended_srl": recommended_srl,
            "reasons": reasons,
            "confidence": successful_reproductions / total_runs if total_runs > 0 else 0.0
        }

def validate_srl_claim(plugin) -> List[str]:
    """Check if a plugin's SRL claim is supported by evidence.
    Returns list of violations."""
    from vireon_core.contracts.plugin import ScientificReadinessLevel
    violations = []
    if plugin.srl >= ScientificReadinessLevel.SRL_4:
        # SRL_4+ requires: empirical validation, reference comparison, published results
        if not plugin.contract.validation_papers:
            violations.append("SRL_4+ requires validation_papers")
        if not plugin.contract.expected_numerical_tolerances:
            violations.append("SRL_4+ requires expected_numerical_tolerances")
    if plugin.srl >= ScientificReadinessLevel.SRL_5:
        # SRL_5 requires: independent reproduction
        if not getattr(plugin, "_independent_reproduction_evidence", None):
            violations.append("SRL_5 requires independent reproduction evidence")
    return violations
