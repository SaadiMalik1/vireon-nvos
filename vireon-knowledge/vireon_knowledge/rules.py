from typing import Any, Callable, Dict, Optional
from pydantic import BaseModel

class IRule(BaseModel):
    """
    An executable scientific or regulatory rule.
    """
    rule_id: str
    description: str
    target_metric: str
    operator: str  # e.g., '>', '<', '==', 'in'
    threshold: Any
    regulatory_reference: Optional[str] = None

    def evaluate(self, measurements: Dict[str, Any]) -> bool:
        if self.target_metric not in measurements:
            return False
            
        val = measurements[self.target_metric]
        if self.operator == '>':
            return val > self.threshold
        elif self.operator == '<':
            return val < self.threshold
        elif self.operator == '>=':
            return val >= self.threshold
        elif self.operator == '<=':
            return val <= self.threshold
        elif self.operator == '==':
            return val == self.threshold
        return False

class FDA_Guidance(IRule):
    """
    A specific machine-readable rule derived from FDA guidance documents.
    """
    guidance_document: str
    section: str
