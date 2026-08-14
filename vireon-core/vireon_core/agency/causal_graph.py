from enum import Enum
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from vireon_core.runtime.rng import DeterministicRNG
from vireon_core.runtime.clock import DeterministicClock, ClockMode

class CausalStage(str, Enum):
    INTENTION = "INTENTION"
    NEURAL_STATE = "NEURAL_STATE"
    SIGNAL = "SIGNAL"
    DECODER_STATE = "DECODER_STATE"
    COMMAND = "COMMAND"
    ACTUATOR_STATE = "ACTUATOR_STATE"
    FEEDBACK = "FEEDBACK"
    UNKNOWN = "UNKNOWN"

class CausalNode(BaseModel):
    id: str
    stage: CausalStage
    timestamp: float
    description: str
    parents: List[str] = Field(default_factory=list)
    is_perturbed: bool = False

class CausalGraph:
    """
    Manages the DAG of causal events for neurotech validation.
    Uses DeterministicClock for reproducible timestamps.
    """
    def __init__(self, seed: int = 42, clock: Optional[DeterministicClock] = None):
        self.nodes: Dict[str, CausalNode] = {}
        self.rng = DeterministicRNG(seed=seed)
        self.clock = clock or DeterministicClock(mode=ClockMode.VIRTUAL, step_dt_ms=1.0)

    def add_node(self, stage: CausalStage, description: str, parents: List[str] = None, is_perturbed: bool = False) -> str:
        node_id = f"node_{self.rng.integer(10000, 99999)}"
        timestamp = self.clock.advance()
        node = CausalNode(
            id=node_id,
            stage=stage,
            timestamp=timestamp,
            description=description,
            parents=parents or [],
            is_perturbed=is_perturbed
        )
        self.nodes[node_id] = node
        return node_id
    
    def get_nodes(self) -> List[CausalNode]:
        return list(self.nodes.values())

