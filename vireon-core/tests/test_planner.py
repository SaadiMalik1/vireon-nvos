import pytest
from vireon_core.planner import plan_experiment

def test_planner_generalize():
    goal = "Determine if my CSP-LDA decoder generalizes across subjects"
    dataset_info = {"source": "data.edf"}
    spec, rationale = plan_experiment(goal, dataset_info, mode="standard")
    
    assert spec.mode == "standard"
    assert spec.validation.strategy == "subject_wise"
    assert "subject_wise" in rationale
    assert spec.dataset.source == "data.edf"
    assert spec.method.algorithm == "csp"

def test_planner_quick():
    goal = "Just run a quick test"
    dataset_info = {"source": "data.edf"}
    spec, rationale = plan_experiment(goal, dataset_info, mode="quick")
    
    assert spec.mode == "quick"
    assert spec.validation.strategy == "single_run"
