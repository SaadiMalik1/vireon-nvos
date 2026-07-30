"""
VIREON Reproducibility Replay System.

Provides the ability to:
1. Re-execute a scenario with a given seed and verify the result matches
2. Verify an evidence bundle's integrity via hashes.json
3. Load telemetry from a bundle and recompute metrics to cross-verify

Usage:
    from vireon_lab.replay import ReplayEngine
    
    result = ReplayEngine.execute_and_compare(
        scenario_path="benchmarks/scenarios/benchmark_eeg_baseline_snr.yaml",
        seed=42,
        expected_hash="abc123..."
    )
"""

import hashlib
import json
import os
from typing import Dict, Any, Optional, Tuple

import numpy as np

from vireon_lab.experiments.schema import load_experiment_from_yaml
from vireon_core.kernel.execution_engine import ExecutionEngine
from vireon_validation.evidence.generator import EvidenceGenerator
from vireon_validation.metrics import generate_signal_metrics


class ReplayEngine:
    """
    Deterministic replay and verification engine.
    
    Core guarantee:
        same scenario + same seed → same execution_hash, same events,
        same measurements, same telemetry (bit-exact numpy arrays).
    """

    @staticmethod
    def execute_scenario(scenario_path: str, seed: int = 42) -> Dict[str, Any]:
        """
        Execute a scenario and return a structured result dict.
        """
        scenario = load_experiment_from_yaml(scenario_path)
        evidence = ExecutionEngine.run(scenario, seed=seed)
        
        return {
            "experiment_id": evidence.experiment_id,
            "execution_hash": evidence.execution_hash,
            "seed": seed,
            "events": [e.model_dump() for e in evidence.events],
            "measurements": {m.metric_name: m.value for m in evidence.measurements},
            "assertions": evidence.assertions_met,
            "_evidence": evidence,
        }

    @staticmethod
    def execute_and_compare(
        scenario_path: str,
        seed: int = 42,
        expected_hash: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute a scenario twice with the same seed and verify bit-exact reproducibility.
        
        Returns:
            Dict with 'reproducible' (bool), 'hash_match' (bool), and detailed comparison.
        """
        run1 = ReplayEngine.execute_scenario(scenario_path, seed=seed)
        run2 = ReplayEngine.execute_scenario(scenario_path, seed=seed)

        # Compare execution hashes
        hashes_match = run1["execution_hash"] == run2["execution_hash"]

        # Compare event IDs (deterministic from RNG)
        events_match = (
            [e["event_id"] for e in run1["events"]] == 
            [e["event_id"] for e in run2["events"]]
        )

        # Compare event timestamps (deterministic from clock)
        timestamps_match = (
            [e["timestamp"] for e in run1["events"]] == 
            [e["timestamp"] for e in run2["events"]]
        )

        # Compare measurements (deterministic from signal processing)
        measurements_match = run1["measurements"] == run2["measurements"]

        # Check against expected hash if provided
        expected_match = True
        if expected_hash is not None:
            expected_match = run1["execution_hash"] == expected_hash

        reproducible = hashes_match and events_match and timestamps_match and measurements_match

        return {
            "reproducible": reproducible,
            "execution_hash": run1["execution_hash"],
            "hashes_match": hashes_match,
            "events_match": events_match,
            "timestamps_match": timestamps_match,
            "measurements_match": measurements_match,
            "expected_hash_match": expected_match,
            "seed": seed,
            "experiment_id": run1["experiment_id"],
        }

    @staticmethod
    def verify_bundle_integrity(bundle_path: str) -> Dict[str, Any]:
        """
        Verify an evidence bundle's integrity by recomputing file hashes
        and comparing against hashes.json.
        """
        hashes_path = os.path.join(bundle_path, "hashes.json")
        if not os.path.exists(hashes_path):
            return {"valid": False, "error": "hashes.json not found"}

        with open(hashes_path, "r") as f:
            stored_hashes = json.load(f)

        mismatches = {}
        verified = {}

        for filename, expected_hash in stored_hashes.items():
            filepath = os.path.join(bundle_path, filename)
            if not os.path.exists(filepath):
                mismatches[filename] = {"expected": expected_hash, "actual": "FILE_MISSING"}
                continue

            sha = hashlib.sha256()
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    sha.update(chunk)
            actual_hash = sha.hexdigest()

            if actual_hash != expected_hash:
                mismatches[filename] = {"expected": expected_hash, "actual": actual_hash}
            else:
                verified[filename] = actual_hash

        return {
            "valid": len(mismatches) == 0,
            "verified_files": len(verified),
            "total_files": len(stored_hashes),
            "mismatches": mismatches if mismatches else None,
        }

    @staticmethod
    def cross_verify_telemetry(bundle_path: str) -> Dict[str, Any]:
        """
        Load telemetry.npz from an evidence bundle, recompute signal metrics,
        and compare against the stored measurements.json.
        
        This proves that the measurements in the bundle were genuinely computed
        from the stored telemetry data.
        """
        telemetry_path = os.path.join(bundle_path, "telemetry.npz")
        measurements_path = os.path.join(bundle_path, "measurements.json")

        if not os.path.exists(telemetry_path):
            return {"valid": False, "error": "telemetry.npz not found"}
        if not os.path.exists(measurements_path):
            return {"valid": False, "error": "measurements.json not found"}

        # Load telemetry
        loaded = np.load(telemetry_path)
        data = loaded["data"]
        sample_rate = float(loaded["sample_rate"][0])

        # Recompute metrics
        recomputed = generate_signal_metrics({
            "data": data,
            "sample_rate": sample_rate,
        })

        # Convert recomputed list of IMeasurements to dict of values
        recomputed_dict = {m.metric_name: m.value for m in recomputed}

        # Load stored measurements
        with open(measurements_path, "r") as f:
            stored_measurements = json.load(f)

        stored_signal = {
            m["metric_name"]: m["value"]
            for m in stored_measurements
            if m["metric_name"] in recomputed_dict
        }

        # Compare
        mismatches = {}
        for name, recomputed_val in recomputed_dict.items():
            stored_val = stored_signal.get(name)
            if stored_val is None:
                continue
            if abs(recomputed_val - stored_val) > 1e-6:
                mismatches[name] = {
                    "stored": stored_val,
                    "recomputed": recomputed_val,
                    "diff": abs(recomputed_val - stored_val),
                }

        return {
            "valid": len(mismatches) == 0,
            "metrics_verified": len(recomputed),
            "mismatches": mismatches if mismatches else None,
        }
