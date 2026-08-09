import pytest
import vireon
from vireon_core.specs.experiment import ExperimentSpec

def test_api_imports():
    assert hasattr(vireon, "validate")
    assert hasattr(vireon, "inspect")
    assert hasattr(vireon, "run")
    assert hasattr(vireon, "report")
    assert hasattr(vireon, "reproduce")
    assert hasattr(vireon, "verify")

def test_validate_quick():
    result = vireon.validate("data.edf", method="csp", mode="quick")
    assert result.spec.mode == "quick"
    assert result.spec.dataset.source == "data.edf"
    assert "⚠ VALIDATION ISSUES" in result.report()

def test_validate_standard():
    result = vireon.validate("data.edf", method="csp", mode="standard")
    assert result.spec.mode == "standard"
    assert result.spec.dataset.source == "data.edf"
    assert "✓ VALIDATED" in result.report()

def test_scorecard_scaling():
    result = vireon.validate("data.edf", method="csp", mode="standard")
    assert result.scorecard is not None
    assert 0 <= result.scorecard.total <= 100
