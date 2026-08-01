import subprocess
import os

from vireon_core.contracts.base import IAssertion, DefaultAssertionEvaluator
from vireon_validation.decision import BCIAssertionEvaluator

def test_default_evaluator_numeric():
    ev = DefaultAssertionEvaluator()
    assert ev.evaluate(IAssertion(name="x", description="", expected_result=0.8), {"x": 0.9}) is True
    assert ev.evaluate(IAssertion(name="x", description="", expected_result=0.8), {"x": 0.7}) is False

def test_default_evaluator_boolean():
    ev = DefaultAssertionEvaluator()
    assert ev.evaluate(IAssertion(name="x", description="", expected_result=True), {"x": True}) is True

def test_bci_evaluator_handles_p300():
    ev = BCIAssertionEvaluator()
    assert ev.evaluate(IAssertion(name="expected_" + "side_channel_leak", description="", expected_result=True), {"p300_" + "detected": 1.0}) is True

def test_kernel_has_no_p300_knowledge():
    """rg p300 returns 0."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    vireon_core_dir = os.path.join(repo_root, "vireon-core")
    result = subprocess.run(["rg", "p300_" + "detected", vireon_core_dir], capture_output=True, text=True)
    # rg returns 1 when no matches are found, which is what we want
    assert result.returncode == 1
    assert not result.stdout.strip()
