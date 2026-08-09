"""vireon_core main package."""
from vireon_core.contracts.base import ISignal, IEvent, IEvidence, ExecutionDAG, DAGNode
from vireon_core.kernel.plugins import PluginManager
from vireon_core.kernel.execution_engine import ExecutionEngine
from vireon_core.runtime.rng import DeterministicRNG
from vireon_core.runtime.clock import DeterministicClock

__version__ = "1.1.0"
__all__ = [
    "ISignal", "IEvent", "IEvidence", "ExecutionDAG", "DAGNode",
    "PluginManager", "ExecutionEngine", "DeterministicRNG", "DeterministicClock"
]
