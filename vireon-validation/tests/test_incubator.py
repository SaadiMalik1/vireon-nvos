import unittest
import numpy as np
from vireon_validation.incubator import run_gauntlet

class DummyPassingPlugin:
    def __init__(self, name="DummyPassing"):
        self.name = name
        self.contract = type("Contract", (), {"validation_papers": ["10.1000/182"]})()

    def execute(self, data):
        return np.asarray(data) * 2.0

class DummyReference:
    def execute(self, data):
        return np.asarray(data) * 2.0

class DummyFailingPlugin:
    def __init__(self, name="DummyFailing"):
        self.name = name
        self.contract = type("Contract", (), {"validation_papers": []})()

    def execute(self, data):
        raise RuntimeError("Crash on execute")

class TestIncubator(unittest.TestCase):
    def test_passing_plugin_gets_srl_4(self):
        plugin = DummyPassingPlugin()
        ref = DummyReference()
        test_data = [np.sin(np.linspace(0, 10, 50))]
        
        result = run_gauntlet(plugin=plugin, test_datasets=test_data, reference_implementations={"reference": ref})
        self.assertEqual(result["srl_recommendation"], "SRL-4")
        self.assertEqual(result["results"]["srl_1"], "PASS")
        self.assertEqual(result["results"]["srl_2"], "PASS")
        self.assertEqual(result["results"]["srl_3"], "PASS")
        self.assertEqual(result["results"]["srl_4"], "PASS")

    def test_failing_plugin_gets_srl_0(self):
        plugin = DummyFailingPlugin()
        test_data = [np.sin(np.linspace(0, 10, 50))]
        
        result = run_gauntlet(plugin=plugin, test_datasets=test_data)
        self.assertEqual(result["srl_recommendation"], "SRL-0")
        self.assertTrue(result["results"]["srl_1"].startswith("FAIL"))

    def test_partial_plugin_without_papers_gets_srl_3(self):
        plugin = DummyPassingPlugin()
        plugin.contract.validation_papers = []
        ref = DummyReference()
        test_data = [np.sin(np.linspace(0, 10, 50))]
        
        result = run_gauntlet(plugin=plugin, test_datasets=test_data, reference_implementations={"reference": ref})
        self.assertEqual(result["srl_recommendation"], "SRL-3")
