"""
M8 — Reproducibility Proof Tests.

These tests formally demonstrate that VIREON produces bit-exact reproducible results:

1. Same scenario + same seed → identical execution hash, events, measurements, telemetry
2. Same scenario + different seed → different results  
3. Evidence bundle integrity verification (hashes.json)
4. Telemetry cross-verification (recompute metrics from stored data)
"""

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
from vireon_lab.replay import ReplayEngine


SCENARIOS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'vireon-validation', 'vireon_validation', 'benchmarks', 'scenarios'))


class TestDeterministicExecution(unittest.TestCase):
    """Test that the execution engine is fully deterministic."""

    def test_same_seed_same_hash(self):
        """Two executions with the same seed must produce the same execution hash."""
        filepath = os.path.join(SCENARIOS_DIR, "01_baseline_eeg.yaml")
        
        scenario1 = load_experiment_from_yaml(filepath)
        evidence1 = ExecutionEngine.run(scenario1, seed=42)
        
        scenario2 = load_experiment_from_yaml(filepath)
        evidence2 = ExecutionEngine.run(scenario2, seed=42)

        self.assertEqual(evidence1.execution_hash, evidence2.execution_hash)

    def test_same_seed_same_events(self):
        """Two executions with the same seed must produce identical event traces."""
        filepath = os.path.join(SCENARIOS_DIR, "benchmark_motor_imagery_erd.yaml")
        
        scenario1 = load_experiment_from_yaml(filepath)
        evidence1 = ExecutionEngine.run(scenario1, seed=99)
        
        scenario2 = load_experiment_from_yaml(filepath)
        evidence2 = ExecutionEngine.run(scenario2, seed=99)
        
        # Event IDs must match (deterministic RNG)
        ids1 = [e.event_id for e in evidence1.events]
        ids2 = [e.event_id for e in evidence2.events]
        self.assertEqual(ids1, ids2)

        # Timestamps must match (deterministic clock)
        ts1 = [e.timestamp for e in evidence1.events]
        ts2 = [e.timestamp for e in evidence2.events]
        self.assertEqual(ts1, ts2)

    def test_same_seed_same_measurements(self):
        """Two executions with the same seed must produce identical measurements."""
        filepath = os.path.join(SCENARIOS_DIR, "benchmark_eeg_artifact_attack.yaml")
        
        scenario1 = load_experiment_from_yaml(filepath)
        evidence1 = ExecutionEngine.run(scenario1, seed=42)
        
        scenario2 = load_experiment_from_yaml(filepath)
        evidence2 = ExecutionEngine.run(scenario2, seed=42)
        
        metrics1 = {m.metric_name: m.value for m in evidence1.measurements}
        metrics2 = {m.metric_name: m.value for m in evidence2.measurements}
        self.assertEqual(metrics1, metrics2)

    def test_same_seed_same_telemetry(self):
        """Two executions with the same seed must produce bit-exact identical numpy data."""
        filepath = os.path.join(SCENARIOS_DIR, "01_baseline_eeg.yaml")
        
        scenario1 = load_experiment_from_yaml(filepath)
        engine1 = ExecutionEngine(scenario1, seed=42)
        engine1.execute()
        
        scenario2 = load_experiment_from_yaml(filepath)
        engine2 = ExecutionEngine(scenario2, seed=42)
        engine2.execute()
        
        data1 = engine1.observations[0].data["data"]
        data2 = engine2.observations[0].data["data"]
        np.testing.assert_array_equal(data1, data2)

    def test_different_seed_different_hash(self):
        """Two executions with different seeds must produce different execution hashes."""
        filepath = os.path.join(SCENARIOS_DIR, "01_baseline_eeg.yaml")
        
        scenario1 = load_experiment_from_yaml(filepath)
        evidence1 = ExecutionEngine.run(scenario1, seed=42)
        
        scenario2 = load_experiment_from_yaml(filepath)
        evidence2 = ExecutionEngine.run(scenario2, seed=999)
        
        self.assertNotEqual(evidence1.execution_hash, evidence2.execution_hash)

    def test_different_seed_different_events(self):
        """Different seeds must produce different event IDs."""
        filepath = os.path.join(SCENARIOS_DIR, "01_baseline_eeg.yaml")
        
        scenario1 = load_experiment_from_yaml(filepath)
        evidence1 = ExecutionEngine.run(scenario1, seed=42)
        
        scenario2 = load_experiment_from_yaml(filepath)
        evidence2 = ExecutionEngine.run(scenario2, seed=999)
        
        ids1 = [e.event_id for e in evidence1.events]
        ids2 = [e.event_id for e in evidence2.events]
        self.assertNotEqual(ids1, ids2)


class TestReplayEngine(unittest.TestCase):
    """Test the replay engine for reproducibility verification."""

    def test_execute_and_compare_reproducible(self):
        """ReplayEngine.execute_and_compare should confirm reproducibility."""
        filepath = os.path.join(SCENARIOS_DIR, "01_baseline_eeg.yaml")
        result = ReplayEngine.execute_and_compare(filepath, seed=42)

        self.assertTrue(result["reproducible"])
        self.assertTrue(result["hashes_match"])
        self.assertTrue(result["events_match"])
        self.assertTrue(result["timestamps_match"])
        self.assertTrue(result["measurements_match"])

    def test_execute_and_compare_with_expected_hash(self):
        """ReplayEngine should match a known execution hash."""
        filepath = os.path.join(SCENARIOS_DIR, "01_baseline_eeg.yaml")
        
        # First, get the hash
        run = ReplayEngine.execute_scenario(filepath, seed=42)
        known_hash = run["execution_hash"]

        # Then verify it matches
        result = ReplayEngine.execute_and_compare(filepath, seed=42, expected_hash=known_hash)
        self.assertTrue(result["expected_hash_match"])

    def test_motor_imagery_reproducible(self):
        """Motor imagery scenario should also be reproducible."""
        filepath = os.path.join(SCENARIOS_DIR, "benchmark_motor_imagery_erd.yaml")
        result = ReplayEngine.execute_and_compare(filepath, seed=77)
        self.assertTrue(result["reproducible"])

    def test_artifact_attack_reproducible(self):
        """Artifact attack scenario should also be reproducible."""
        filepath = os.path.join(SCENARIOS_DIR, "benchmark_eeg_artifact_attack.yaml")
        result = ReplayEngine.execute_and_compare(filepath, seed=123)
        self.assertTrue(result["reproducible"])

    def test_mock_provider_reproducible(self):
        """Legacy mock provider scenarios should also be reproducible."""
        filepath = os.path.join(SCENARIOS_DIR, "benchmark_false_activation.yaml")
        result = ReplayEngine.execute_and_compare(filepath, seed=42)
        self.assertTrue(result["reproducible"])


class TestBundleIntegrity(unittest.TestCase):
    """Test evidence bundle integrity verification."""

    def test_verify_untampered_bundle(self):
        """An untampered evidence bundle should pass integrity verification."""
        filepath = os.path.join(SCENARIOS_DIR, "01_baseline_eeg.yaml")
        scenario = load_experiment_from_yaml(filepath)
        engine = ExecutionEngine(scenario, seed=42)
        evidence = engine.execute()
        raw_data = engine.observations[0].data if engine.observations else None
        
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = EvidenceGenerator(evidence, tmpdir)
            bundle_path = gen.generate_bundle(raw_provider_data=raw_data)

            result = ReplayEngine.verify_bundle_integrity(bundle_path)
            self.assertTrue(result["valid"])
            self.assertGreater(result["verified_files"], 4)
            self.assertIsNone(result["mismatches"])

    def test_detect_tampered_bundle(self):
        """A tampered evidence bundle should fail integrity verification."""
        filepath = os.path.join(SCENARIOS_DIR, "01_baseline_eeg.yaml")
        scenario = load_experiment_from_yaml(filepath)
        engine = ExecutionEngine(scenario, seed=42)
        evidence = engine.execute()
        raw_data = engine.observations[0].data if engine.observations else None
        
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = EvidenceGenerator(evidence, tmpdir)
            bundle_path = gen.generate_bundle(raw_provider_data=raw_data)

            # Tamper with measurements.json
            measurements_file = os.path.join(bundle_path, "measurements.json")
            with open(measurements_file, "w") as f:
                json.dump([{"metric_name": "fake", "value": 999.0, "unit": "fake"}], f)

            result = ReplayEngine.verify_bundle_integrity(bundle_path)
            self.assertFalse(result["valid"])
            self.assertIn("measurements.json", result["mismatches"])

    def test_bundle_contains_environment(self):
        """Evidence bundle should contain environment.json."""
        filepath = os.path.join(SCENARIOS_DIR, "01_baseline_eeg.yaml")
        scenario = load_experiment_from_yaml(filepath)
        engine = ExecutionEngine(scenario, seed=42)
        evidence = engine.execute()
        raw_data = engine.observations[0].data if engine.observations else None
        
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = EvidenceGenerator(evidence, tmpdir)
            bundle_path = gen.generate_bundle(raw_provider_data=raw_data)

            env_path = os.path.join(bundle_path, "environment.json")
            self.assertTrue(os.path.exists(env_path))

            with open(env_path) as f:
                env = json.load(f)
            self.assertIn("python_version", env)
            self.assertIn("numpy_version", env)
            self.assertIn("platform", env)

    def test_bundle_contains_hashes(self):
        """Evidence bundle should contain hashes.json with all file checksums."""
        filepath = os.path.join(SCENARIOS_DIR, "01_baseline_eeg.yaml")
        scenario = load_experiment_from_yaml(filepath)
        engine = ExecutionEngine(scenario, seed=42)
        evidence = engine.execute()
        raw_data = engine.observations[0].data if engine.observations else None
        
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = EvidenceGenerator(evidence, tmpdir)
            bundle_path = gen.generate_bundle(raw_provider_data=raw_data)

            hashes_path = os.path.join(bundle_path, "hashes.json")
            self.assertTrue(os.path.exists(hashes_path))

            with open(hashes_path) as f:
                hashes = json.load(f)
            self.assertIn("manifest.json", hashes)
            self.assertIn("events.json", hashes)
            self.assertIn("measurements.json", hashes)
            self.assertIn("environment.json", hashes)
            self.assertIn("telemetry.npz", hashes)


class TestTelemetryCrossVerification(unittest.TestCase):
    """Test that stored telemetry matches stored measurements."""

    def test_cross_verify_real_telemetry(self):
        """Recomputing metrics from stored telemetry.npz should match measurements.json."""
        filepath = os.path.join(SCENARIOS_DIR, "01_baseline_eeg.yaml")
        scenario = load_experiment_from_yaml(filepath)
        engine = ExecutionEngine(scenario, seed=42)
        evidence = engine.execute()
        raw_data = engine.observations[0].data if engine.observations else None
        
        with tempfile.TemporaryDirectory() as tmpdir:
            gen = EvidenceGenerator(evidence, tmpdir)
            bundle_path = gen.generate_bundle(raw_provider_data=raw_data)

            result = ReplayEngine.cross_verify_telemetry(bundle_path)
            self.assertTrue(result["valid"])
            self.assertGreater(result["metrics_verified"], 5)
            self.assertIsNone(result["mismatches"])

    def test_two_bundles_identical(self):
        """Two bundles from same seed should have identical hashes.json content."""
        filepath = os.path.join(SCENARIOS_DIR, "01_baseline_eeg.yaml")

        with tempfile.TemporaryDirectory() as tmpdir1, tempfile.TemporaryDirectory() as tmpdir2:
            scenario1 = load_experiment_from_yaml(filepath)
            engine1 = ExecutionEngine(scenario1, seed=42)
            evidence1 = engine1.execute()
            raw_data1 = engine1.observations[0].data if engine1.observations else None
            gen1 = EvidenceGenerator(evidence1, tmpdir1)
            bundle1 = gen1.generate_bundle(raw_provider_data=raw_data1)

            scenario2 = load_experiment_from_yaml(filepath)
            engine2 = ExecutionEngine(scenario2, seed=42)
            evidence2 = engine2.execute()
            raw_data2 = engine2.observations[0].data if engine2.observations else None
            gen2 = EvidenceGenerator(evidence2, tmpdir2)
            bundle2 = gen2.generate_bundle(raw_provider_data=raw_data2)

            # Load hashes from both bundles
            with open(os.path.join(bundle1, "hashes.json")) as f:
                hashes1 = json.load(f)
            with open(os.path.join(bundle2, "hashes.json")) as f:
                hashes2 = json.load(f)

            # All file hashes should be identical
            self.assertEqual(hashes1, hashes2)


if __name__ == "__main__":
    unittest.main()

class TestM1EndToEndProof(unittest.TestCase):
    """
    Phase III: Deterministic Validation Kernel (M1 — First End-to-End Proof).
    Explicitly tests that baseline.no_op.001 runs successfully and reproducibly.
    """
    def test_baseline_noop_deterministic(self):
        filepath = os.path.join(SCENARIOS_DIR, "baseline_noop_001.yaml")
        scenario = load_experiment_from_yaml(filepath)
        
        from vireon_validation.agency import AgencyValidator
        from vireon_validation.metrics import generate_signal_metrics
        evidence1 = ExecutionEngine.run(
            scenario, seed=123,
            agency_validator_cls=AgencyValidator,
            signal_metrics_func=generate_signal_metrics
        )
        evidence2 = ExecutionEngine.run(
            scenario, seed=123,
            agency_validator_cls=AgencyValidator,
            signal_metrics_func=generate_signal_metrics
        )
        
        # M1 criteria: same seed yields identical execution hash
        self.assertEqual(evidence1.execution_hash, evidence2.execution_hash)
        
        # M1 criteria: Event trace generated
        self.assertGreater(len(evidence1.events), 0)
        
        # M1 criteria: Evidence bundle has measurements
        self.assertGreater(len(evidence1.measurements), 0)

        # M1 criteria: Execution context is recorded
        self.assertIsNotNone(evidence1.execution_context)
        self.assertEqual(evidence1.execution_context.experiment_id, "baseline.no_op.001")
        self.assertEqual(evidence1.execution_context.deterministic_seed, 123)
        self.assertEqual(evidence1.execution_context.provider_metadata.get("provider_type"), "MockProvider")
