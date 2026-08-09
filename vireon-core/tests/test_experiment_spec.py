import pytest
from vireon_core.specs.experiment import ExperimentSpec
from vireon_core.specs.presets import quick_spec, standard_spec, research_spec

def test_quick_spec():
    spec = quick_spec("data.edf", "csp")
    assert spec.mode == "quick"
    assert spec.dataset.source == "data.edf"
    assert spec.method.algorithm == "csp"
    
def test_mode_consistency_invalid():
    with pytest.raises(ValueError, match="Quick mode does not support robustness testing"):
        spec = quick_spec("data.edf", "csp")
        spec.robustness = {"perturbations": []}
        spec.validate_mode_consistency()

def test_yaml_roundtrip(tmp_path):
    spec = quick_spec("data.edf", "csp")
    yaml_str = spec.to_yaml()
    yaml_path = tmp_path / "spec.yaml"
    yaml_path.write_text(yaml_str)
    
    loaded = ExperimentSpec.from_yaml(str(yaml_path))
    assert loaded.mode == "quick"
    assert loaded.dataset.source == "data.edf"
    assert loaded.method.algorithm == "csp"
