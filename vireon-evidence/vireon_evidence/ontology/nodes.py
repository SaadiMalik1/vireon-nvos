from pydantic import BaseModel
from typing import Optional, List, Dict, Any

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
    rmse: Optional[float]
    icc: Optional[float]
    status: str
    
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

