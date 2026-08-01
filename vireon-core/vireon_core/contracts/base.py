from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
import uuid

class IScientificObject(BaseModel):
    """
    Base object for all typed scientific entities in NVOS.
    Plugins pass these objects through the generic kernel DAG.
    """
    object_id: str = ""
    object_type: str = "IScientificObject"
    calibration_provenance: Dict[str, str] = {}
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.object_id:
            self.object_id = str(uuid.uuid4())

class IDataset(IScientificObject):
    object_type: str = "IDataset"
    name: str

class ISignal(IScientificObject):
    object_type: str = "ISignal"
    sampling_rate: float
    data: Any

class IDevice(IScientificObject):
    object_type: str = "IDevice"
    model_name: str

class IDisease(IScientificObject):
    object_type: str = "IDisease"
    icd_code: Optional[str] = None

class IBiomarker(IScientificObject):
    object_type: str = "IBiomarker"
    description: str

class IMethod(IScientificObject):
    object_type: str = "IMethod"
    name: str

class IKnowledgeNode(IScientificObject):
    object_type: str = "IKnowledgeNode"
    iri: str

class IValidationResult(IScientificObject):
    object_type: str = "IValidationResult"
    passed: bool

class IPublication(IScientificObject):
    object_type: str = "IPublication"
    doi: str

class IProvider(ABC):
    """
    Abstract base for any neurotechnology provider (e.g., OpenBCI, PiEEG, Synthetic).
    """
    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    def get_data(self) -> Any:
        pass

class IStimulus(IScientificObject):
    """
    Defines the stimulus or intent applied during a scenario (e.g., an intended action or adversarial perturbation).
    """
    object_type: str = "IStimulus"
    type: str
    parameters: Dict[str, Any]

class IUncertainty(BaseModel):
    """
    Multidimensional provenanced uncertainty representation.
    """
    mean: float
    variance: float
    distribution: str
    confidence_interval: Optional[list[float]] = None
    sample_size: int
    method: str

class IObservation(IScientificObject):
    """
    An observation captured from the execution of the scenario.
    """
    object_type: str = "IObservation"
    timestamp: float
    data_source: str
    data: Any
    uncertainty: Optional[IUncertainty] = None

class IEvent(IScientificObject):
    """
    A node in the causal event trace.
    """
    object_type: str = "IEvent"
    event_id: str
    timestamp: float
    description: str
    causal_stage: str = "UNKNOWN"
    causal_parents: List[str] = []
    is_perturbed: bool = False
    uncertainty: Optional[IUncertainty] = None

class IAssertion(IScientificObject):
    """
    A specific claim to be validated by the scenario execution.
    """
    object_type: str = "IAssertion"
    name: str
    description: str
    expected_result: Any

class IMeasurement(IScientificObject):
    """
    A quantified metric resulting from the scenario execution.
    """
    object_type: str = "IMeasurement"
    metric_name: str
    value: float
    unit: str
    uncertainty: Optional[IUncertainty] = None

class IExecutionContext(BaseModel):
    """
    The deterministic execution context for an experiment.
    """
    experiment_id: str

    deterministic_seed: int
    provider_metadata: Dict[str, Any]
    version_info: str
    environment_fingerprint: str
    git_sha: Optional[str] = None
    dependency_versions: Optional[Dict[str, str]] = None
    os_info: Optional[str] = None
    cpu_info: Optional[str] = None
    gpu_info: Optional[str] = None
    compiler_info: Optional[str] = None
    blas_implementation: Optional[str] = None
    random_seed_state: Optional[Dict[str, Any]] = None

class IDecision(IScientificObject):
    """
    The scientific conclusion drawn from the evidence.
    """
    object_type: str = "IDecision"
    passed: bool
    confidence: float
    reasoning: str
    recommended_next_step: str
    uncertainty_bounds: Optional[IUncertainty] = None

class IEvidenceQuality(IScientificObject):
    """
    FAIR-aligned metrics assessing the overall validity and traceability of the evidence bundle.
    """
    object_type: str = "IEvidenceQuality"
    completeness: float
    numerical_integrity: float
    statistical_robustness: float
    scientific_validity: float
    traceability: float
    reproducibility: float
    external_agreement: float
    standards_compliance: float
    overall: float

class IEvidence(IScientificObject):
    """
    The reproducible evidence bundle generated after executing a scenario.
    """
    object_type: str = "IEvidence"
    experiment_id: str
    execution_hash: str
    execution_context: IExecutionContext
    telemetry_path: str
    events: List[IEvent]
    measurements: List[IMeasurement]
    assertions_met: Dict[str, bool]
    json_ld_schema: Optional[Dict[str, Any]] = None
    hypothesis: Optional[str] = None
    experiment_design: Optional[str] = None
    methodology: Optional[str] = None
    algorithm: Optional[str] = None
    decision: Optional[IDecision] = None
    validation_graph: Optional[Dict[str, Any]] = None
    evidence_quality: Optional[IEvidenceQuality] = None

class IExperimentDef(ABC):
    """
    The declarative specification of an experiment (formerly IScenario).
    """
    @abstractmethod
    def get_provider(self) -> IProvider:
        pass

    @abstractmethod
    def get_stimulus(self) -> List[IStimulus]:
        pass

    @abstractmethod
    def get_assertions(self) -> List[IAssertion]:
        pass

from enum import Enum

class SignalType(str, Enum):
    EEG = "EEG"
    ECOG = "ECOG"
    LFP = "LFP"
    SEEG = "SEEG"
    MEG = "MEG"
    EMG = "EMG"
    EOG = "EOG"
    ECG = "ECG"
    FNIRS = "FNIRS"
    SPIKE = "SPIKE"
    UNKNOWN = "UNKNOWN"

class IExperiment(IScientificObject):
    """
    The canonical root object representing an entire execution lifecycle.
    """
    object_type: str = "IExperiment"
    
    # Expanded Provenance Graph
    research_question: str = ""
    hypothesis: str = ""
    experimental_design: str = ""
    dataset_id: Optional[str] = None
    method_id: Optional[str] = None
    execution_hash: str = ""
    evidence_id: Optional[str] = None
    statistical_analysis: str = ""
    decision_id: Optional[str] = None
    publication_id: Optional[str] = None
    independent_replication: Optional[str] = None
    
    signal_type: SignalType = SignalType.UNKNOWN
    experiment_def: IExperimentDef
    threat_model: List[str] = []
    validation_protocol: List[str] = []
    results: List[IMeasurement] = []
    evidence_bundle: Optional[IEvidence] = None
    decision: Optional[IDecision] = None

    model_config = {"arbitrary_types_allowed": True}

class DAGNode(BaseModel):
    node_id: str
    stage: str
    plugin_id: Optional[str] = None
    inputs: List[str] = []
    config: Dict[str, Any] = {}

class ExecutionDAG(BaseModel):
    nodes: List[DAGNode]

    @classmethod
    def from_stages(cls, stages: Optional[List[str]] = None) -> 'ExecutionDAG':
        if stages is None:
            stages = ["INTENTION", "NEURAL_STATE", "SIGNAL", "DECODER_STATE", "COMMAND", "ACTUATOR_STATE", "FEEDBACK"]
        nodes = []
        for i, stage in enumerate(stages):
            node_id = f"stage_{i}"
            inputs = [f"stage_{i-1}"] if i > 0 else []
            nodes.append(DAGNode(node_id=node_id, stage=stage, inputs=inputs))
        return cls(nodes=nodes)

    def validate_dag(self):
        node_map = {n.node_id: n for n in self.nodes}
        roots = []
        import graphlib
        graph = {}
        for n in self.nodes:
            if not n.inputs:
                roots.append(n.node_id)
            graph[n.node_id] = []
            for inp in n.inputs:
                if inp not in node_map:
                    raise ValueError(f"Input '{inp}' for node '{n.node_id}' does not exist.")
                graph[n.node_id].append(inp)
                
        ts = graphlib.TopologicalSorter(graph)
        try:
            tuple(ts.static_order())
        except graphlib.CycleError as e:
            raise ValueError(f"ExecutionDAG contains a cycle: {e}")

        if len(roots) != 1:
            raise ValueError("ExecutionDAG must have exactly one root.")

    def model_post_init(self, __context: Any) -> None:
        self.validate_dag()

