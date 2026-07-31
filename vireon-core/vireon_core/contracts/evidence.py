from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

class SoftwareProvenance(BaseModel):
    vireon_version: str
    python_version: str
    os_info: str
    dependencies: Dict[str, str]

class DatasetProvenance(BaseModel):
    dataset_id: str
    doi: Optional[str]
    bids_version: str
    download_url: Optional[str]
    hash_checksum: str

class MethodProvenance(BaseModel):
    plugin_id: str
    version: str
    srl: str
    scientific_contract_hash: str
    
class EnvironmentFingerprint(BaseModel):
    hardware_info: Dict[str, str]
    random_seed: int
    execution_timestamp: datetime = Field(default_factory=datetime.utcnow)

class EvidenceBundle(BaseModel):
    """
    Evidence Bundle 2.0 (Publication-Quality Research Artifact)
    """
    bundle_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    bundle_hash: str = Field(default="")
    cryptographic_signature: str = Field(default="")
    graph_commit_id: str = Field(default="")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    conclusion_verdict: str
    dataset_provenance: DatasetProvenance
    software_provenance: SoftwareProvenance
    method_provenance: List[MethodProvenance]
    environment: EnvironmentFingerprint
    input_hashes: Dict[str, str]
    output_hashes: Dict[str, str]
    statistical_agreement: Dict[str, float]
    benchmark_results: Dict[str, Any]
    figures: Dict[str, str] # e.g., Base64 or Paths to ROC, spectra
