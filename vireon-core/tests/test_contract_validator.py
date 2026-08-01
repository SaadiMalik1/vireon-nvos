import pytest
import numpy as np
from vireon_core.contracts.plugin import ContractValidator, ScientificContractViolation
from vireon_methods.base import WelchPSD
from vireon_core.contracts.base import ExecutionDAG, DAGNode
from vireon_core.kernel.execution_engine import ExecutionEngine
from vireon_core.kernel.plugins import PluginManager

@pytest.fixture
def welch_plugin():
    return WelchPSD(nperseg=256)

def test_nan_input_raises_violation(welch_plugin):
    signal = np.array([1.0, np.nan, 3.0])
    with pytest.raises(ScientificContractViolation, match="NaN"):
        ContractValidator.validate(welch_plugin, {"signal": signal})

def test_inf_input_raises_violation(welch_plugin):
    signal = np.array([1.0, np.inf, 3.0])
    with pytest.raises(ScientificContractViolation, match="Inf"):
        ContractValidator.validate(welch_plugin, {"signal": signal})

def test_short_signal_raises_violation(welch_plugin):
    signal = np.zeros(100)  # nperseg=256
    with pytest.raises(ScientificContractViolation, match="nperseg"):
        ContractValidator.validate(welch_plugin, {"signal": signal})

def test_nonstationary_signal_raises_violation(welch_plugin):
    # Signal with strong trend (non-stationary)
    t = np.arange(10000)
    signal = 0.1 * t + np.random.default_rng(42).normal(size=t.shape)
    with pytest.raises(ScientificContractViolation, match="Stationarity"):
        ContractValidator.validate(welch_plugin, {"signal": signal})

def test_valid_input_does_not_raise(welch_plugin):
    signal = np.random.default_rng(42).normal(size=1024)
    ContractValidator.validate(welch_plugin, {"signal": signal})  # no exception

class MockProvider:
    def start(self): pass
    def stop(self): pass
    def get_data(self): return {"data": np.array([1.0, np.nan, 3.0])}

class MockExperiment:
    def get_provider(self): return MockProvider()
    def get_stimulus(self): return []
    def get_assertions(self): return []

def test_engine_logs_violation_does_not_crash():
    """When a contract is violated, the engine logs it and continues."""
    pm = PluginManager()
    pm.register_plugin(WelchPSD(nperseg=256), config={})
    from vireon_core.contracts.plugin import IPlugin, ScientificContract, ScientificReadinessLevel
    from vireon_core.contracts.base import ISignal
    
    class BadProducer(IPlugin):
        @property
        def plugin_id(self): return "bad.producer"
        @property
        def version(self): return "1.0"
        @property
        def srl(self): return ScientificReadinessLevel.SRL_0
        @property
        def contract(self): return ScientificContract()
        @property
        def capabilities(self): return []
        @property
        def inputs(self): return []
        @property
        def outputs(self): return []
        @property
        def plugin_type(self): return "method"
        def initialize(self, config): pass
        def execute(self, inputs):
            return {"signal": ISignal(sampling_rate=1.0, data=np.array([1.0, np.nan, 3.0]))}
            
    pm.register_plugin(BadProducer(), config={})
    
    dag = ExecutionDAG(nodes=[
        DAGNode(node_id="n0", stage="SIGNAL", plugin_id="bad.producer"),
        DAGNode(node_id="n1", stage="DECODER_STATE", plugin_id="vk:Method:Welch", inputs=["n0"]),
    ])

    engine = ExecutionEngine(experiment=MockExperiment(), plugin_manager=pm)
    result = engine.execute(dag=dag)
    
    # Assert engine doesn't crash and we get a CONTRACT_VIOLATION event
    violation_events = [e for e in result.events if "CONTRACT_VIOLATION" in e.description]
    assert len(violation_events) > 0
    assert "NaN" in violation_events[0].description
