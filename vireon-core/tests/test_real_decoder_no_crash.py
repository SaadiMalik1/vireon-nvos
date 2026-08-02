import pytest
import numpy as np
from vireon_core.contracts.base import ExecutionDAG, DAGNode
from vireon_core.kernel.execution_engine import ExecutionEngine
from vireon_core.kernel.plugins import PluginManager
from vireon_methods.decoding.sklearn_lda_plugin import SklearnLDAPlugin

class MockProvider:
    def start(self): pass
    def stop(self): pass
    def get_data(self): return {"data": np.array([[1.0, 2.0], [3.0, 4.0]])}

class MockExperiment:
    def get_provider(self): return MockProvider()
    def get_stimulus(self): return []
    def get_assertions(self): return []

def test_real_sklearn_decoder_does_not_crash_unfitted():
    """Unfitted SklearnLDAPlugin in a DAG must not crash with ValueError."""
    plugin = SklearnLDAPlugin()
    assert not getattr(plugin, '_fitted', False)
    
    dag = ExecutionDAG(nodes=[
        DAGNode(node_id="sig", stage="SIGNAL"),
        DAGNode(node_id="dec", stage="DECODER_STATE", plugin_id="method_decoding_sklearn_lda", inputs=["sig"]),
    ])
    pm = PluginManager()
    pm.register_plugin(plugin, config={})
    engine = ExecutionEngine(experiment=MockExperiment(), plugin_manager=pm)
    
    result = engine.execute(dag=dag)
    assert result is not None
    assert engine.node_outputs["dec"] is None

def test_fitted_sklearn_decoder_executes_predict():
    """Fitted SklearnLDAPlugin in a DAG successfully calls predict."""
    plugin = SklearnLDAPlugin()
    X_train = np.array([[1.0, 2.0], [2.0, 3.0], [8.0, 9.0], [9.0, 10.0]])
    y_train = np.array([0, 0, 1, 1])
    plugin.fit(X_train, y_train)
    
    dag = ExecutionDAG(nodes=[
        DAGNode(node_id="sig", stage="SIGNAL"),
        DAGNode(node_id="dec", stage="DECODER_STATE", plugin_id="method_decoding_sklearn_lda", inputs=["sig"]),
    ])
    pm = PluginManager()
    pm.register_plugin(plugin, config={})
    engine = ExecutionEngine(experiment=MockExperiment(), plugin_manager=pm)
    
    result = engine.execute(dag=dag)
    assert result is not None
    assert engine.node_outputs["dec"] is not None
