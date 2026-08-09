import pytest
from vireon_core.specs.experiment import ExperimentSpec
from vireon_core.specs.presets import quick_spec, standard_spec, research_spec
from vireon_core.specs.validator import SpecValidator

def test_valid_spec():
    spec = standard_spec("data.edf", "csp")
    validator = SpecValidator()
    issues = validator.validate(spec)
    assert len(issues) == 0

def test_invalid_quick_strategy():
    spec = quick_spec("data.edf", "csp")
    spec.validation.strategy = "k_fold"
    validator = SpecValidator()
    issues = validator.validate(spec)
    assert len(issues) > 0
    assert issues[0].severity == "error"
    assert "not allowed in 'quick' mode" in issues[0].message

def test_invalid_perturbation():
    spec = research_spec("data.edf", "csp")
    spec.robustness.perturbations[0].severity = 1.5
    validator = SpecValidator()
    issues = validator.validate(spec)
    assert len(issues) > 0
    assert issues[0].severity == "error"
    assert "between 0.0 and 1.0" in issues[0].message
