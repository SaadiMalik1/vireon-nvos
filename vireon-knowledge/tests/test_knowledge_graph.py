import os
import networkx as nx
from vireon_knowledge.engine import KnowledgeGraph
from vireon_core.kernel.execution_engine import ExecutionEngine
from vireon_core.contracts.base import IExperimentDef, IProvider, ExecutionDAG, DAGNode
from vireon_core.kernel.plugins import PluginManager

def test_knowledge_graph_loading():
    kg_root = os.path.join(os.path.dirname(__file__), "..", "vireon_knowledge")
    kg = KnowledgeGraph(kg_root)
    
    # Check that networkx graph was created and nodes populated
    assert isinstance(kg.graph, nx.DiGraph)
    assert len(kg.graph.nodes) > 0
    
    # Check for a specific method and rule
    assert "vk:Method:Welch" in kg.graph
    assert "vk:Rule:StationarityForWelch" in kg.graph
    
    # Check edge exists
    assert kg.graph.has_edge("vk:Method:Welch", "vk:Rule:StationarityForWelch")

def test_validate_methodology_violations():
    kg_root = os.path.join(os.path.dirname(__file__), "..", "vireon_knowledge")
    kg = KnowledgeGraph(kg_root)
    
    # Test violation (stationarity = False for Welch)
    observed = {"signal.stationarity": False}
    violations = kg.validate_methodology("vk:Method:Welch", observed)
    
    assert len(violations) > 0
    assert violations[0]["rule"] == "vk:Rule:StationarityForWelch"
    
    # Test no violation (stationarity = True for Welch)
    observed_pass = {"signal.stationarity": True}
    violations_pass = kg.validate_methodology("vk:Method:Welch", observed_pass)
    
    assert len(violations_pass) == 0

class DummyExperiment(IExperimentDef):
    def get_provider(self) -> IProvider:
        class DummyProvider(IProvider):
            def start(self): pass
            def stop(self): pass
            def get_data(self): return {"data": None}
        return DummyProvider()
    
    def get_assertions(self):
        return []
        
    def get_stimulus(self):
        return []

class DummyPlugin:
    def __init__(self, plugin_id):
        self.plugin_id = plugin_id
        
    def execute(self, inputs):
        return {"output": "ok"}
        
    @property
    def contract(self):
        from vireon_core.contracts.plugin import ScientificContract
        return ScientificContract()

def test_execution_engine_calls_kg():
    # Setup mock ExecutionEngine with KnowledgeGraph
    kg_root = os.path.join(os.path.dirname(__file__), "..", "vireon_knowledge")
    kg = KnowledgeGraph(kg_root)
    
    experiment = DummyExperiment()
    pm = PluginManager()
    
    # Add dummy plugin matching Welch method
    pm._plugins["vk:Method:Welch"] = DummyPlugin("vk:Method:Welch")
    
    dag = ExecutionDAG(nodes=[
        DAGNode(node_id="test_node", stage="SIGNAL", plugin_id="vk:Method:Welch", inputs=[])
    ])
    
    engine = ExecutionEngine(experiment, plugin_manager=pm, knowledge_graph=kg)
    
    # Mock node outputs to trigger a violation condition in the DAG loop
    # We will inject the observed state into the node_outputs for "test_node" inputs
    # Wait, the node inputs will be empty dict.
    
    # Just running it, we will see if KNOWLEDGE_VIOLATION event is logged.
    # Since inputs_dict is empty, signal.stationarity is None -> False -> violation.
    evidence = engine.execute(dag)
    
    # Find KNOWLEDGE_VIOLATION event
    violation_events = [e for e in evidence.events if "KNOWLEDGE_VIOLATION" in e.description]
    assert len(violation_events) > 0
    assert "Welch's method is inappropriate" in violation_events[0].description
