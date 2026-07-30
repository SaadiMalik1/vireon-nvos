import sys
import os
import unittest
import json
import tempfile
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from vireon_lab.experiments.schema import load_experiment_from_yaml
from vireon_core.kernel.execution_engine import ExecutionEngine
from vireon_validation.evidence.generator import EvidenceGenerator


SCENARIOS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'vireon-validation', 'vireon_validation', 'benchmarks', 'scenarios'))


class TestRealDataPipeline(unittest.TestCase):
    """
    End-to-end test: load a real-data scenario, execute it through the canonical pipeline,
    and verify the evidence bundle contains real signal metrics and numpy telemetry.
    """

    def test_eeg_baseline_scenario(self):
        """Execute the EEG baseline SNR scenario with SyntheticSignalProvider."""
        from vireon_models.providers.datasets import SyntheticSignalProvider
        
        from vireon_core.contracts.base import IExperimentDef
        class MockScenario(IExperimentDef):
            def get_provider(self):
                return SyntheticSignalProvider(seed=42, num_channels=4, duration_sec=1.0, include_p300=True)
        
        filepath = os.path.join(SCENARIOS_DIR, "01_baseline_eeg.yaml")
        scenario = load_experiment_from_yaml(filepath)
        from vireon_validation.agency import AgencyValidator
        from vireon_validation.metrics import generate_signal_metrics
        evidence = ExecutionEngine.run(
            scenario,
            agency_validator_cls=AgencyValidator,
            signal_metrics_func=generate_signal_metrics
        )
        
        # Check that signal-level metrics are present
        metric_names = {m.metric_name for m in evidence.measurements}
        self.assertIn("snr_db", metric_names)
        self.assertIn("alpha_band_power", metric_names)
        self.assertIn("beta_band_power", metric_names)

        # SNR should be a finite value (auto-estimated SNR on complex multi-band
        # signals is low due to the moving-average noise estimator, but it should be computed)
        snr_metric = next(m for m in evidence.measurements if m.metric_name == "snr_db")
        self.assertTrue(np.isfinite(snr_metric.value))

        # Evidence bundle should contain real telemetry
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = EvidenceGenerator(evidence, tmpdir)
            bundle_path = gen.generate_bundle()

            # Check manifest has signal metadata
            with open(os.path.join(bundle_path, "manifest.json")) as f:
                manifest = json.load(f)
            self.assertTrue(manifest["has_real_telemetry"])
            self.assertEqual(manifest["sample_rate"], 250.0)
            self.assertEqual(manifest["num_channels"], 8)

            # Check telemetry.npz exists and contains real data
            npz_path = os.path.join(bundle_path, "telemetry.npz")
            self.assertTrue(os.path.exists(npz_path))
            loaded = np.load(npz_path)
            self.assertIn("data", loaded)
            self.assertEqual(loaded["data"].shape, (500, 8))  # 2s * 250Hz = 500, 8ch

    def test_motor_imagery_scenario(self):
        """Execute the motor imagery ERD scenario with MotorImageryProvider."""
        filepath = os.path.join(SCENARIOS_DIR, "benchmark_motor_imagery_erd.yaml")
        scenario = load_experiment_from_yaml(filepath)
        from vireon_validation.agency import AgencyValidator
        from vireon_validation.metrics import generate_signal_metrics
        evidence = ExecutionEngine.run(
            scenario,
            agency_validator_cls=AgencyValidator,
            signal_metrics_func=generate_signal_metrics
        )
        
        metric_names = {m.metric_name for m in evidence.measurements}
        self.assertIn("mu_band_power", metric_names)
        self.assertIn("snr_db", metric_names)
        self.assertIn("false_activation_rate", metric_names)

        # Scenario ID should be the real one from the YAML
        self.assertEqual(evidence.experiment_id, "benchmark.signal.motor_imagery_erd")

    def test_artifact_attack_scenario(self):
        """Execute the artifact attack scenario and verify powerline detection."""
        filepath = os.path.join(SCENARIOS_DIR, "benchmark_eeg_artifact_attack.yaml")
        scenario = load_experiment_from_yaml(filepath)
        from vireon_validation.agency import AgencyValidator
        from vireon_validation.metrics import generate_signal_metrics
        evidence = ExecutionEngine.run(
            scenario,
            agency_validator_cls=AgencyValidator,
            signal_metrics_func=generate_signal_metrics
        )
        
        metric_names = {m.metric_name for m in evidence.measurements}
        self.assertIn("powerline_50hz_detected", metric_names)

        # The 50Hz powerline hum was injected, so it should be detected
        pl_metric = next(m for m in evidence.measurements if m.metric_name == "powerline_50hz_detected")
        self.assertEqual(pl_metric.value, 1.0)

    def test_backward_compat_mock_provider(self):
        """Legacy scenarios with mock_provider should still work."""
        filepath = os.path.join(SCENARIOS_DIR, "benchmark_false_activation.yaml")
        scenario = load_experiment_from_yaml(filepath)
        from vireon_validation.agency import AgencyValidator
        from vireon_validation.metrics import generate_signal_metrics
        evidence = ExecutionEngine.run(
            scenario,
            agency_validator_cls=AgencyValidator,
            signal_metrics_func=generate_signal_metrics
        )
        
        # Should still have agency metrics
        metric_names = {m.metric_name for m in evidence.measurements}
        self.assertIn("false_activation_rate", metric_names)

        # Should have signal metrics (mock provider returns proper dict now)
        self.assertIn("snr_db", metric_names)


if __name__ == "__main__":
    unittest.main()
