import pytest
from vireon_validation.decision import StringConstraintEvaluator
from vireon_core.contracts.base import IMeasurement
from unittest.mock import Mock

def test_string_constraint_evaluator_pass():
    measurements = [
        IMeasurement(metric_name="accuracy", value=0.9, unit=""),
        IMeasurement(metric_name="loss", value=0.1, unit="")
    ]
    expected = {
        "accuracy": "> 0.8",
        "loss": "< 0.2",
        "label": 1.0
    }
    
    measurements.append(IMeasurement(metric_name="label", value=1.0, unit=""))
    
    evidence_quality = Mock()
    evidence_quality.overall = 1.0
    
    decision = StringConstraintEvaluator.evaluate(measurements, expected, evidence_quality)
    
    assert decision.passed is True
    assert decision.confidence == 100.0
    assert "accuracy (0.9000) met condition > 0.8" in decision.reasoning
    assert "loss (0.1000) met condition < 0.2" in decision.reasoning

def test_string_constraint_evaluator_fail():
    measurements = [
        IMeasurement(metric_name="accuracy", value=0.7, unit=""),
    ]
    expected = {
        "accuracy": "> 0.8"
    }
    
    evidence_quality = Mock()
    evidence_quality.overall = 0.8
    
    decision = StringConstraintEvaluator.evaluate(measurements, expected, evidence_quality)
    
    assert decision.passed is False
    assert decision.confidence == 40.0 # 80.0 * 0.5 penalty
    assert "accuracy (0.7000) failed condition > 0.8" in decision.reasoning
