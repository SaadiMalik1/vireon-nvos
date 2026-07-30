"""
Evidence Bundle Generator.

Serializes an IEvidence object into the reproducible evidence bundle format:
    manifest.json     — scenario metadata, signal config, execution hash
    events.json       — full causal event trace
    measurements.json — all metrics (agency + signal)
    assertions.json   — pass/fail assertions
    environment.json  — execution environment (Python, numpy, OS versions)
    telemetry.npz     — raw numpy signal data (if real provider)
    hashes.json       — SHA-256 of every file in the bundle for integrity verification
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Dict
from vireon_core.contracts import IEvidence
from vireon_validation.evidence.environment import capture_environment


class EvidenceGenerator:
    """
    Serializes an IEvidence object into the reproducible evidence bundle format.
    """
    def __init__(self, evidence: IEvidence, output_dir: str):
        self.evidence = evidence
        self.output_dir = Path(output_dir)

    def generate_bundle(self) -> str:
        run_dir = self.output_dir / f"run_{self.evidence.execution_hash}"
        run_dir.mkdir(parents=True, exist_ok=True)

        raw_data = getattr(self.evidence, '_raw_provider_data', None)

        # Write manifest
        manifest = {
            "scenario_id": self.evidence.scenario_id,
            "execution_hash": self.evidence.execution_hash,
            "execution_context": self.evidence.execution_context.model_dump(),
            "version": "1.0.0"
        }

        # Enrich manifest with signal metadata if available
        if isinstance(raw_data, dict):
            manifest["sample_rate"] = raw_data.get("sample_rate")
            manifest["num_channels"] = raw_data.get("num_channels")
            manifest["duration_sec"] = raw_data.get("duration_sec")
            manifest["seed"] = raw_data.get("seed")
            manifest["has_real_telemetry"] = True
        else:
            manifest["has_real_telemetry"] = False

        with open(run_dir / "manifest.json", "w") as f:
            json.dump(manifest, f, indent=2)

        # Write Events
        events_data = [e.model_dump() for e in self.evidence.events]
        with open(run_dir / "events.json", "w") as f:
            json.dump(events_data, f, indent=2)

        # Write Measurements
        measurements_data = [m.model_dump() for m in self.evidence.measurements]
        with open(run_dir / "measurements.json", "w") as f:
            json.dump(measurements_data, f, indent=2)

        # Write Assertions
        with open(run_dir / "assertions.json", "w") as f:
            json.dump(self.evidence.assertions_met, f, indent=2)

        # Write environment
        environment = capture_environment()
        with open(run_dir / "environment.json", "w") as f:
            json.dump(environment, f, indent=2)

        # Write telemetry
        self._write_telemetry(str(run_dir), raw_data)

        # Write integrity hashes (must be last — hashes all other files)
        hashes = self._compute_bundle_hashes(str(run_dir))
        with open(run_dir / "hashes.json", "w") as f:
            json.dump(hashes, f, indent=2)

        return str(run_dir)

    def _write_telemetry(self, bundle_dir: str, raw_data):
        """Write telemetry as numpy .npz if real data, otherwise write a stub."""
        import numpy as np

        telemetry_path = os.path.join(bundle_dir, "telemetry.npz")

        if isinstance(raw_data, dict) and isinstance(raw_data.get("data"), np.ndarray):
            # Real telemetry: save the numpy array with metadata
            np.savez_compressed(
                telemetry_path,
                data=raw_data["data"],
                sample_rate=np.array([raw_data.get("sample_rate", 250.0)]),
                num_channels=np.array([raw_data.get("num_channels", 1)]),
            )
        else:
            # Stub for backward compatibility with mock providers
            stub_path = os.path.join(bundle_dir, "telemetry.parquet")
            with open(stub_path, "w") as f:
                f.write("PARQUET_STUB_DATA")

    @staticmethod
    def _compute_bundle_hashes(bundle_dir: str) -> Dict[str, str]:
        """
        Compute SHA-256 of every file in the bundle directory (except hashes.json itself).
        This allows independent verification that the bundle hasn't been tampered with.
        """
        hashes = {}
        for filename in sorted(os.listdir(bundle_dir)):
            if filename == "hashes.json":
                continue
            filepath = os.path.join(bundle_dir, filename)
            if os.path.isfile(filepath):
                sha = hashlib.sha256()
                with open(filepath, "rb") as f:
                    for chunk in iter(lambda: f.read(8192), b""):
                        sha.update(chunk)
                hashes[filename] = sha.hexdigest()
        return hashes
