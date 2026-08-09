from pydantic import BaseModel
from typing import Optional, Dict, Any

class EvidenceNode(BaseModel):
    node_id: str
    node_type: str
    metadata: Dict[str, Any] = {}

class DatasetNode(EvidenceNode):
    node_type: str = "Dataset"
    bids_version: str
    doi: Optional[str]

class MethodNode(EvidenceNode):
    node_type: str = "Method"
    canonical_name: str
    version: str

class BenchmarkNode(EvidenceNode):
    node_type: str = "Benchmark"
    target_metric: str
    
class EvidenceBundleNode(EvidenceNode):
    node_type: str = "EvidenceBundle"
    rmse: Optional[float] = None
    icc: Optional[float] = None
    status: str = "PASS"

    @classmethod
    def from_evidence_bundle(cls, bundle: "EvidenceBundle") -> "EvidenceBundleNode":
        """Factory method to construct EvidenceBundleNode from a core EvidenceBundle."""
        metrics = bundle.metrics or {}
        rmse_val = metrics.get("rmse") if metrics.get("rmse") is not None else None
        icc_val = metrics.get("icc") if metrics.get("icc") is not None else None
        
        meta = {
            "algorithm": bundle.algorithm,
            "reference": bundle.reference,
            "dataset": bundle.dataset,
            "srl_recommendation": bundle.srl_recommendation,
            "runtime_sec": bundle.runtime_sec,
            "memory_mb": bundle.memory_mb,
            "metrics": metrics,
            **bundle.model_dump(exclude={"bundle_id", "pass_fail", "metrics"})
        }
        return cls(
            node_id=bundle.bundle_id,
            rmse=rmse_val,
            icc=icc_val,
            status=bundle.pass_fail,
            metadata=meta
        )

    def to_evidence_bundle(self) -> "EvidenceBundle":
        """Converts EvidenceBundleNode back into core EvidenceBundle."""
        from vireon_core.contracts.evidence import EvidenceBundle
        meta = dict(self.metadata)
        metrics = meta.pop("metrics", {})
        if self.rmse is not None and "rmse" not in metrics:
            metrics["rmse"] = self.rmse
        if self.icc is not None and "icc" not in metrics:
            metrics["icc"] = self.icc
            
        algorithm = meta.pop("algorithm", "")
        dataset = meta.pop("dataset", "")
        reference = meta.pop("reference", "")
        srl = meta.pop("srl_recommendation", "SRL-1")
        runtime_sec = meta.pop("runtime_sec", 0.0)
        memory_mb = meta.pop("memory_mb", 0.0)
        
        # Construct bundle
        return EvidenceBundle(
            bundle_id=self.node_id,
            algorithm=algorithm,
            reference=reference,
            dataset=dataset,
            pass_fail=self.status,
            srl_recommendation=srl,
            runtime_sec=runtime_sec,
            memory_mb=memory_mb,
            metrics=metrics,
            **{k: v for k, v in meta.items() if hasattr(EvidenceBundle, k) or k in EvidenceBundle.model_fields}
        )
    
class ScientificClaimNode(EvidenceNode):
    node_type: str = "ScientificClaim"
    claim_description: str
    confidence_score: float
    verdict: str

class PublicationNode(EvidenceNode):
    node_type: str = "Publication"
    doi: str
    title: str

class MathematicalAssumptionNode(EvidenceNode):
    node_type: str = "MathematicalAssumption"
    assumption_text: str

class SignalTypeNode(EvidenceNode):
    node_type: str = "SignalType"
    modality: str

class HardwareNode(EvidenceNode):
    node_type: str = "Hardware"
    device_name: str

class ConsensusNode(EvidenceNode):
    node_type: str = "ScientificConsensus"
    consensus_statement: str

class ClinicalApplicationNode(EvidenceNode):
    node_type: str = "ClinicalApplication"
    disease_or_task: str

