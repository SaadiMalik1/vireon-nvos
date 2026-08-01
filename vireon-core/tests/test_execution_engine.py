import pytest
from vireon_core.contracts.base import ExecutionDAG, DAGNode
from vireon_core.kernel.execution_engine import ExecutionEngine

class MockProvider:
    def start(self): pass
    def stop(self): pass
    def get_data(self): return {"data": [1,2,3]}

class MockExperiment:
    def get_provider(self): return MockProvider()
    def get_stimulus(self): return []
    def get_assertions(self): return []

def test_engine_initializes_with_default_dag():
    """Execution engine runs default stages if no DAG provided."""
    engine = ExecutionEngine(experiment=MockExperiment())
    result = engine.execute()
    assert result.execution_hash is not None
    
    stages_seen = [e.causal_stage for e in result.events]
    assert "INTENTION" in stages_seen
    assert "FEEDBACK" in stages_seen
    assert len(stages_seen) == 7
