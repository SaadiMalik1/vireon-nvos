import numpy as np
from vireon_validation.benchmarks.matrix import BenchmarkMatrix

class MockDataset:
    def __init__(self):
        self.data = np.zeros(100)
        self.labels = np.zeros(100)
        self.doi = "10.test.doi"
        
class MockMethod:
    def __init__(self, returns=None, raises=None):
        self.returns = returns
        self.raises = raises
        self.execute_called = False
        self.plugin_id = "mock.method"
        
    def execute(self, inputs):
        self.execute_called = True
        if self.raises:
            raise self.raises
        return self.returns

def test_matrix_calls_method_execute():
    mock_method = MockMethod(returns=np.zeros(100))
    matrix = BenchmarkMatrix()
    matrix.add_method(mock_method)
    matrix.add_dataset("test", MockDataset())
    
    bundles = matrix.execute_matrix()
    
    assert mock_method.execute_called
    assert bundles[0]["method_provenance"][0]["plugin_id"] == "mock.method"
    
def test_matrix_records_failure():
    failing_method = MockMethod(raises=ValueError("boom"))
    matrix = BenchmarkMatrix()
    matrix.add_method(failing_method)
    matrix.add_dataset("test", MockDataset())
    
    bundles = matrix.execute_matrix()
    
    assert bundles[0]["success"] is False
    assert "boom" in bundles[0]["error"]
    
def test_matrix_computes_real_ccc():
    matrix = BenchmarkMatrix()
    # If the method returns slightly noisy data, CCC won't be 0.95 or exactly 1
    class NoisyMethod:
        plugin_id = "noisy"
        def execute(self, inputs):
            return inputs["signal"] + np.random.normal(scale=0.1, size=inputs["signal"].shape)
            
    matrix.add_method(NoisyMethod())
    matrix.add_dataset("test", MockDataset())
    
    bundles = matrix.execute_matrix()
    
    ccc = bundles[0]["statistical_agreement"]["ccc"]
    assert abs(ccc - 0.94999) > 1e-5
    assert bundles[0]["benchmark_results"]["execution_time_sec"] > 0
