from typing import List, Dict, Any
from vireon_core.contracts.base import IMeasurement, IDecision, IAssertion, DefaultAssertionEvaluator

class BCIAssertionEvaluator(DefaultAssertionEvaluator):
    def evaluate(self, assertion: IAssertion, measurements: dict) -> bool:
        if assertion.name == "expected_side_channel_leak":
            p300 = measurements.get("p300_detected", 0.0)
            return bool(p300) == bool(assertion.expected_result)
        return super().evaluate(assertion, measurements)

class StringConstraintEvaluator:
    """
    Evaluates evidence bundles and produces an explicit scientific conclusion.
    """
    
    @classmethod
    def evaluate(cls, measurements: List[IMeasurement], expected: Dict[str, Any], evidence_quality: Any) -> IDecision:
        """
        Produce a PASS/FAIL decision based on the evidence metrics and the expected constraints.
        Computes a confidence score based on the provided Evidence Quality.
        """
        metrics = {m.metric_name: m.value for m in measurements}
        
        passed = True
        reasons = []
        evaluated_constraints = 0
        total_constraints = len(expected)
        
        for key, expected_val in expected.items():
            # simple string-based evaluation constraint handling
            if isinstance(expected_val, str) and (">" in expected_val or "<" in expected_val or "=" in expected_val):
                parts = expected_val.strip().split(" ")
                if len(parts) == 2:
                    op, target = parts
                    metric_name = key
                elif len(parts) == 3:
                    metric_name, op, target = parts
                else:
                    reasons.append(f"Failed to parse expected constraint: {expected_val}")
                    continue
                    
                try:
                    target = float(target)
                    actual = metrics.get(metric_name)
                    
                    if actual is None:
                        passed = False
                        reasons.append(f"Metric '{metric_name}' not found.")
                        continue
                        
                    evaluated_constraints += 1
                    
                    # Evaluating conditions
                    condition_met = True
                    if op == ">" and not (actual > target): condition_met = False
                    elif op == ">=" and not (actual >= target): condition_met = False
                    elif op == "<" and not (actual < target): condition_met = False
                    elif op == "<=" and not (actual <= target): condition_met = False
                    elif op == "==" and not (actual == target): condition_met = False
                    
                    if not condition_met:
                        passed = False
                        reasons.append(f"{metric_name} ({actual:.4f}) failed condition {op} {target}")
                    else:
                        reasons.append(f"{metric_name} ({actual:.4f}) met condition {op} {target}")
                        
                except ValueError:
                    reasons.append(f"Failed to parse target value: {target}")
            
            else:
                # Direct equality match
                actual = metrics.get(key)
                if actual is None:
                    passed = False
                    reasons.append(f"Metric '{key}' not found.")
                    continue
                
                evaluated_constraints += 1
                if actual != expected_val:
                    passed = False
                    reasons.append(f"{key} was {actual}, expected {expected_val}")
                else:
                    reasons.append(f"{key} matched expected {expected_val}")
                    
        confidence = evidence_quality.overall * 100.0
        
        # Penalize if it explicitly failed
        if not passed:
            confidence = confidence * 0.5
            
        reasoning = "; ".join(reasons) if reasons else "No constraints evaluated."
        next_step = "Proceed to next campaign" if passed else "Investigate failure reasons and debug"
        
        return IDecision(
            passed=passed,
            confidence=round(confidence, 2),
            reasoning=reasoning,
            recommended_next_step=next_step
        )
