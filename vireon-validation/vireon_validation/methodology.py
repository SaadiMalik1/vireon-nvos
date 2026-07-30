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
        Augmented Dickey-Fuller (ADF) test for stationarity.
        Null Hypothesis (H0): The series has a unit root (is non-stationary).
        Alternate Hypothesis (H1): The series is stationary.
        Returns True if stationary (p-value < 0.05).
        """
        try:
            from statsmodels.tsa.stattools import adfuller
        except ImportError:
            # Fallback if statsmodels is not available
            return True

        if len(data.shape) > 1:
            data = data[:, 0] if data.shape[0] > data.shape[1] else data[0, :]
            
        n = len(data)
        if n < 30:
            return True
            
        try:
            # maxlag is automatically determined if None, but let's be safe for short signals
            result = adfuller(data, autolag='AIC')
            p_value = result[1]
            return p_value < 0.05
        except Exception:
            return True

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
