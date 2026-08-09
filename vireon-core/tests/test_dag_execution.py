import pytest
from vireon_core.contracts.base import ExecutionDAG, DAGNode
from vireon_core.kernel.execution_engine import ExecutionEngine
from vireon_core.kernel.plugins import PluginManager
from vireon_core.contracts.plugin import IPlugin, ScientificContract, ScientificReadinessLevel

class MockPlugin(IPlugin):
    def __init__(self, returns):
        self._returns = returns
        
    @property
    def plugin_id(self): return "mock.plugin"
    @property
    def version(self): return "1.0.0"
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
    def plugin_type(self): return "mock"
    
    def initialize(self, config): pass
    def execute(self, inputs): return self._returns

def test_dag_topological_order():
    """Nodes execute in topological order."""
    dag = ExecutionDAG(nodes=[
        DAGNode(node_id="a", stage="INTENTION"),
        DAGNode(node_id="b", stage="SIGNAL", inputs=["a"]),
        DAGNode(node_id="c", stage="DECODER_STATE", inputs=["a"]),
        DAGNode(node_id="d", stage="COMMAND", inputs=["b", "c"]),
    ])
    order = ExecutionEngine._topological_order(dag)
    assert order.index("a") < order.index("b")
    assert order.index("a") < order.index("c")
    assert order.index("b") < order.index("d")
    assert order.index("c") < order.index("d")

def test_dag_cycle_detection():
    """A cyclic DAG raises ValueError."""
    # We construct a cyclic graph directly because validation might catch it on init.
    with pytest.raises(ValueError, match="cycle"):
        dag = ExecutionDAG(nodes=[
            DAGNode(node_id="a", stage="INTENTION", inputs=["c"]),
            DAGNode(node_id="b", stage="SIGNAL", inputs=["a"]),
            DAGNode(node_id="c", stage="DECODER_STATE", inputs=["b"]),
        ])

class MockProvider:
    def start(self): pass
    def stop(self): pass
    def get_data(self): return {"data": [1,2,3]}

class MockExperiment:
    def get_provider(self): return MockProvider()
    def get_stimulus(self): return []
    def get_assertions(self): return []

def test_plugin_node_calls_execute():
    """A node with plugin_id calls plugin.execute()."""
    mock_plugin = MockPlugin(returns="hello")
    pm = PluginManager()
    pm.register_plugin(mock_plugin, config={})
    
    dag = ExecutionDAG(nodes=[
        DAGNode(node_id="n1", stage="SIGNAL", plugin_id="mock.plugin"),
    ])
    
    engine = ExecutionEngine(experiment=MockExperiment(), plugin_manager=pm)
    result = engine.execute(dag=dag)
    assert engine.node_outputs["n1"] == "hello"

def test_linear_dag_backward_compat():
    """The old 7-stage linear flow still works."""
    dag = ExecutionDAG.from_stages(["INTENTION", "NEURAL_STATE", "SIGNAL", "DECODER_STATE", "COMMAND", "ACTUATOR_STATE", "FEEDBACK"])
    engine = ExecutionEngine(experiment=MockExperiment())
    result = engine.execute(dag=dag)
    
    # Check that events were generated for the stages
    stages_seen = [e.causal_stage for e in result.events]
    assert "INTENTION" in stages_seen
    assert "FEEDBACK" in stages_seen

def test_execution_hash_includes_node_outputs():
    """Changing a node's output changes the hash."""
    pm1 = PluginManager()
    pm1.register_plugin(MockPlugin(returns="result_A"), config={})
    engine1 = ExecutionEngine(experiment=MockExperiment(), plugin_manager=pm1)
    dag = ExecutionDAG(nodes=[DAGNode(node_id="n1", stage="SIGNAL", plugin_id="mock.plugin")])
    res1 = engine1.execute(dag=dag)

    pm2 = PluginManager()
    pm2.register_plugin(MockPlugin(returns="result_B"), config={})
    engine2 = ExecutionEngine(experiment=MockExperiment(), plugin_manager=pm2)
    res2 = engine2.execute(dag=dag)

    assert res1.execution_hash != res2.execution_hash
