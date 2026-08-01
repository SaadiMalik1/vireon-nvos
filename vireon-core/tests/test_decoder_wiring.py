import pytest
import numpy as np
from vireon_core.contracts.base import ExecutionDAG, DAGNode
from vireon_core.kernel.execution_engine import ExecutionEngine
from vireon_core.kernel.plugins import PluginManager
from vireon_core.contracts.decoder import IDecoder, DecoderNotFittedError
from vireon_methods.decoding.sklearn_lda_plugin import SklearnLDAPlugin

class MockDecoder(IDecoder):
    def __init__(self, returns):
        super().__init__()
        self._returns = returns
        self.predict_called = False
        
    @property
    def plugin_id(self): return "mock.decoder"
    @property
    def version(self): return "1.0.0"
    
    def initialize(self, config): pass
    def execute(self, inputs): return self._returns
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        super().fit(X, y)

    def predict(self, X: np.ndarray) -> np.ndarray:
        super().predict(X)
        self.predict_called = True
        return self._returns

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        super().predict_proba(X)
        return self._returns

class MockProvider:
    def start(self): pass
    def stop(self): pass
    def get_data(self): return {"data": [1,2,3]}

class MockExperiment:
    def get_provider(self): return MockProvider()
    def get_stimulus(self): return []
    def get_assertions(self): return []

def test_decoder_plugin_is_called():
    """A DECODER_STATE node with a decoder plugin calls predict()."""
    mock_decoder = MockDecoder(returns="left_hand")
    pm = PluginManager()
    pm.register_plugin(mock_decoder, config={})
    dag = ExecutionDAG(nodes=[
        DAGNode(node_id="sig", stage="SIGNAL"),
        DAGNode(node_id="dec", stage="DECODER_STATE", plugin_id="mock.decoder", inputs=["sig"]),
    ])
    engine = ExecutionEngine(experiment=MockExperiment(), plugin_manager=pm)
    result = engine.execute(dag=dag)
    assert mock_decoder.predict_called
    assert engine.node_outputs["dec"] == "left_hand"

def test_decoder_stage_without_plugin_logs_skipped():
    """A DECODER_STATE node with no plugin logs 'skipped' not 'processed'."""
    dag = ExecutionDAG(nodes=[
        DAGNode(node_id="dec", stage="DECODER_STATE"),
    ])
    engine = ExecutionEngine(experiment=MockExperiment())
    result = engine.execute(dag=dag)
    
    # Check events to see if skipped was logged
    decoder_events = [e for e in result.events if "DECODER_STATE" in e.description or "Decoder" in e.description]
    descriptions = [e.description for e in decoder_events]
    assert any("skipped" in d for d in descriptions)
    assert not any("Decoder processed signal" in d for d in descriptions)

def test_predict_before_fit_raises():
    """Calling predict before fit raises DecoderNotFittedError."""
    decoder = MockDecoder(returns="left_hand")
    # By default, mock decoder isn't fitted.
    with pytest.raises(DecoderNotFittedError):
        decoder.predict(np.array([]))

def test_sklearn_lda_is_decoder():
    """SklearnLDAPlugin passes isinstance(plugin, IDecoder)."""
    plugin = SklearnLDAPlugin()
    assert isinstance(plugin, IDecoder)
