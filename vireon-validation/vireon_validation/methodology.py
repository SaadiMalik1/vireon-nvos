from typing import Dict, Any, List
from vireon_knowledge.engine import KnowledgeGraph
from vireon_methods.base import IMethodology
import numpy as np
import scipy.stats

class MethodologicalValidator:
    """
    Evaluates observed signal properties against the explicitly declared
    required assumptions of the target algorithm, using the Knowledge Graph.
    """
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.kg = knowledge_graph
        
    def _test_stationarity(self, data: np.ndarray) -> bool:
        """
        Simple Augmented Dickey-Fuller proxy or basic variance stationarity test.
        For demonstration, we check if the variance of the first half is similar to the second half.
        """
        if len(data.shape) > 1:
            data = data[0] # use first channel
        n = len(data)
        if n < 100:
            return True
            
        var_1 = np.var(data[:n//2])
        var_2 = np.var(data[n//2:])
        
        # If variance changes by more than 50%, it's non-stationary
        if min(var_1, var_2) == 0:
            return False
            
        ratio = max(var_1, var_2) / min(var_1, var_2)
        return ratio < 1.5

    def validate(self, method: IMethodology, data: np.ndarray) -> Dict[str, Any]:
        """
        Runs empirical property tests on the data, then asks the Knowledge Graph
        if the method's assumptions are satisfied.
        """
        observed_properties = {
            "is_stationary": self._test_stationarity(data),
            # Add more empirical tests here (e.g. is_independent, is_gaussian)
            "is_independent": True 
        }
        
        return self.kg.evaluate_methodology(method.method_id, observed_properties)
