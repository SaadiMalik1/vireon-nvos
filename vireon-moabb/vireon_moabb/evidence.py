"""
EvidenceAssembler — creates a cryptographic EvidenceBundle from execution traces.

Key principle (ADR 0008 #8): Every evidence claim must trace to an execution artifact.
This assembler creates a SHA-256 bundle that contains:
- The experiment spec
- The execution trace (dataset, partitions, results, environment)
- The validation results
- A content hash that ties them all together

No hardcoded hashes. No fake metrics. Every number in the bundle was actually executed.
"""
import hashlib
import json
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from typing import Any

from vireon_moabb.executor import MoabbExecutionTrace
from vireon_moabb.validation import ValidationResult


@dataclass
class EvidenceBundle:
    """A cryptographic evidence bundle.

    The evidence_hash is a SHA-256 over the entire bundle content (spec + trace + validation).
    Changing any field changes the hash.
    """
    bundle_id: str
    evidence_hash: str
    created_at: str
    experiment_spec: dict[str, Any]
    execution_trace: dict[str, Any]
    validation_results: dict[str, Any]
    # Summary fields for quick reference
    summary: dict[str, Any]

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(asdict(self), indent=indent, default=str)

    def save(self, path: str) -> str:
        """Save the bundle to a JSON file. Returns the path."""
        with open(path, "w") as f:
            f.write(self.to_json())
        return path

    def verify(self) -> bool:
        """Verify that the evidence hash matches the bundle content.

        ADDED in playbook dx — was specified in playbook but not implemented.
        Recomputes the SHA-256 over spec + trace + validation + summary and
        compares to the stored evidence_hash.

        Returns:
            True if hash matches (bundle is intact), False if tampered.
        """
        hash_payload = {
            "experiment_spec": self.experiment_spec,
            "execution_trace": self.execution_trace,
            "validation_results": self.validation_results,
            "summary": self.summary,
        }
        hash_content = json.dumps(hash_payload, sort_keys=True, default=str)
        expected_hash = hashlib.sha256(hash_content.encode("utf-8")).hexdigest()
        return expected_hash == self.evidence_hash


class EvidenceAssembler:
    """Assembles an EvidenceBundle from execution traces and validation results."""

    def assemble(
        self,
        spec_dict: dict[str, Any],
        trace: MoabbExecutionTrace,
        validation: ValidationResult,
    ) -> EvidenceBundle:
        """Create an EvidenceBundle.

        Args:
            spec_dict: The ExperimentSpec as a dict.
            trace: The MoabbExecutionTrace from the executor.
            validation: The ValidationResult from the validation layer.

        Returns:
            EvidenceBundle with SHA-256 hash.
        """
        created_at = datetime.now(timezone.utc).isoformat()

        # Summary for quick reference
        summary = {
            "experiment_name": spec_dict.get("name", ""),
            "experiment_goal": spec_dict.get("goal", ""),
            "mode": spec_dict.get("mode", ""),
            "dataset": trace.dataset_metadata.dataset_class,
            "n_subjects": trace.dataset_metadata.n_subjects,
            "n_folds": len(trace.fold_results),
            "mean_accuracy": trace.mean_accuracy,
            "chance_level": 1.0 / trace.dataset_metadata.n_classes if trace.dataset_metadata.n_classes > 0 else 0.5,
            "all_validation_passed": validation.all_passed,
            "moabb_version": trace.environment.moabb_version,
            "seed": trace.seed,
        }

        # Build the bundle content for hashing
        trace_dict = trace.to_dict()
        validation_dict = validation.to_dict()

        # Compute content hash
        # The hash covers: spec + trace (without moabb_warnings for stability) + validation + summary
        hash_payload = {
            "experiment_spec": spec_dict,
            "execution_trace": trace_dict,
            "validation_results": validation_dict,
            "summary": summary,
        }
        hash_content = json.dumps(hash_payload, sort_keys=True, default=str)
        evidence_hash = hashlib.sha256(hash_content.encode("utf-8")).hexdigest()

        # Bundle ID (short hash for human reference)
        bundle_id = f"vireon-{evidence_hash[:12]}"

        return EvidenceBundle(
            bundle_id=bundle_id,
            evidence_hash=evidence_hash,
            created_at=created_at,
            experiment_spec=spec_dict,
            execution_trace=trace_dict,
            validation_results=validation_dict,
            summary=summary,
        )
