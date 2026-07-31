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

class RegulatoryProfile(BaseModel):
    fda_gmlp_compliance: str = Field(default="")
    iec_62304_class: str = Field(default="")
    iso_14971_risk_mapped: bool = Field(default=False)
    iec_60601_applicable: bool = Field(default=False)

class EvidenceBundle(BaseModel):
    """
    Evidence Bundle 5.0 (Scientific Ecosystem & Regulatory Readiness)
    """
    # Identifiers & Hashes
    bundle_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    evidence_hash: str = Field(default="")
    replay_hash: str = Field(default="")
    graph_commit_id: str = Field(default="")
    cryptographic_signature: str = Field(default="")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Benchmarking Topology
    algorithm: str = Field(default="")
    reference: str = Field(default="")
    dataset: str = Field(default="")
    campaign_class: str = Field(default="") # e.g. Robustness, Numerical Precision, Reproducibility
    workflow_id: str = Field(default="") # e.g. pipeline_motor_imagery_v1
    
    perturbation: str = Field(default="")
    hardware: str = Field(default="")
    random_seed: int = Field(default=42)
    
    # Methodology & Assumptions
    scientific_contract: str = Field(default="")
    assumptions: List[str] = Field(default_factory=list)
    known_limitations: List[str] = Field(default_factory=list)
    
    # Clinical Domain Validation
    clinical_domains_supported: List[str] = Field(default_factory=list)
    clinical_domains_unsupported: List[str] = Field(default_factory=list)
    
    # Quantitative Results
    runtime_sec: float = Field(default=0.0)
    memory_mb: float = Field(default=0.0)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    
    # Performance Profiling (Scaling)
    runtime_scaling: Dict[str, Any] = Field(default_factory=dict)
    memory_scaling: Dict[str, Any] = Field(default_factory=dict)
    cpu_utilization: float = Field(default=0.0)
    parallelization_efficiency: float = Field(default=0.0)
    
    # Domain: Connectivity
    connectivity_metric: str = Field(default="")
    estimator: str = Field(default="")
    network_density: float = Field(default=0.0)
    graph_statistics: Dict[str, float] = Field(default_factory=dict)
    
    # Domain: Imaging & Source Localization
    head_model: str = Field(default="")
    coordinate_system: str = Field(default="")
    leadfield_checksum: str = Field(default="")
    localization_error_mm: float = Field(default=0.0)
    resolution_matrix: Dict[str, Any] = Field(default_factory=dict)
    uncertainty_quantification: Dict[str, Any] = Field(default_factory=dict) # Covariance, credible regions
    
    # Scientific Verdict
    acceptance_criteria: Dict[str, Any] = Field(default_factory=dict)
    pass_fail: str = Field(default="FAIL")
    srl_recommendation: str = Field(default="SRL-1")
    scientific_reproducibility_index: float = Field(default=0.0) # SRI Score (Phase E)
    
    # Regulatory Mapping
    regulatory_profile: RegulatoryProfile = Field(default_factory=lambda: RegulatoryProfile(fda_gmlp_compliance="", iec_62304_class="", iso_14971_risk_mapped=False, iec_60601_applicable=False))
    
    # Reporting Artifacts
    notebook_path: str = Field(default="")
    report_path: str = Field(default="")
    
    # Legacy fields (maintained for backward compat)
    conclusion_verdict: str = Field(default="")
    dataset_provenance: DatasetProvenance = Field(default_factory=lambda: DatasetProvenance(dataset_id="", bids_version="", hash_checksum="", doi="", download_url=""))
    software_provenance: SoftwareProvenance = Field(default_factory=lambda: SoftwareProvenance(vireon_version="", python_version="", os_info="", dependencies={}))
    method_provenance: List[MethodProvenance] = Field(default_factory=list)
    environment: EnvironmentFingerprint = Field(default_factory=lambda: EnvironmentFingerprint(hardware_info={}, random_seed=42))
    input_hashes: Dict[str, str] = Field(default_factory=dict)
    output_hashes: Dict[str, str] = Field(default_factory=dict)
    statistical_agreement: Dict[str, float] = Field(default_factory=dict)
    benchmark_results: Dict[str, Any] = Field(default_factory=dict)
    figures: Dict[str, str] = Field(default_factory=dict) # e.g., Base64 or Paths to ROC, spectra
