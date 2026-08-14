from typing import List
from pydantic import BaseModel
from vireon_core.contracts.base import IEvidence
from vireon_knowledge.rules import IRule

class DecisionTrace(BaseModel):
    """
    A single trace entry explaining a decision rule outcome.
    """
    rule_id: str
    description: str
    status: str
    measurement_used: float
    regulatory_reference: str = "None"

class DecisionResult(BaseModel):
    """
    The output of the Decision Engine.
    """
    status: str  # PASS / FAIL
    confidence: float
    reason: str
    traces: List[DecisionTrace]
    missing_evidence: List[str]

class DecisionEngine:
    """
    Evaluates evidence against executable knowledge rules to produce 
    traceable, regulatory-grade decisions.
    """
    def __init__(self, rules: List[IRule]):
        self.rules = rules

    def evaluate(self, evidence: IEvidence) -> DecisionResult:
        traces = []
        all_passed = True
        missing = []
        
        # Convert list of measurements to dict
        measurement_dict = {m.metric_name: m.value for m in evidence.measurements}

        for rule in self.rules:
            if rule.target_metric not in measurement_dict:
                all_passed = False
                missing.append(rule.target_metric)
                traces.append(
                    DecisionTrace(
                        rule_id=rule.rule_id,
                        description=rule.description,
                        status="MISSING_DATA",
                        measurement_used=0.0,
                        regulatory_reference=rule.regulatory_reference or "None"
                    )
                )
                continue
                
            passed = rule.evaluate(measurement_dict)
            if not passed:
                all_passed = False
                
            traces.append(
                DecisionTrace(
                    rule_id=rule.rule_id,
                    description=rule.description,
                    status="PASS" if passed else "FAIL",
                    measurement_used=measurement_dict[rule.target_metric],
                    regulatory_reference=rule.regulatory_reference or "None"
                )
            )

        status = "PASS" if all_passed and not missing else "FAIL"
        
        return DecisionResult(
            status=status,
            confidence=1.0 if all_passed else 0.0,
            reason="All validation rules satisfied." if all_passed else "One or more rules failed.",
            traces=traces,
            missing_evidence=missing
        )
