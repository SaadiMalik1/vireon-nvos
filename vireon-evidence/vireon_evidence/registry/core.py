import sqlite3
import json
import hashlib
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from vireon_core.contracts.evidence import EvidenceBundle
from vireon_evidence.exceptions import EvidenceAlreadyRegisteredError


class EvidenceRegistry:
    """Evidence Registry with SQLite backend for persisting and querying evidence bundles.

    Uses append-only INSERT OR IGNORE semantics to prevent silent overwrites.
    """

    def __init__(self, db_path: str = "evidence_registry.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS bundles (
                evidence_hash TEXT PRIMARY KEY,
                bundle JSON,
                timestamp TEXT,
                algorithm TEXT,
                dataset TEXT
            )
        """)
        self.conn.commit()

    def _get_bundle_json(self, evidence_hash: str) -> Optional[str]:
        cursor = self.conn.execute(
            "SELECT bundle FROM bundles WHERE evidence_hash=?",
            (evidence_hash,)
        )
        row = cursor.fetchone()
        return row[0] if row else None

    def get(self, evidence_hash: str) -> Optional[EvidenceBundle]:
        return self.retrieve(evidence_hash)

    def register(self, bundle: Any) -> str:
        """Register an evidence bundle. Raises if hash already exists with different content."""
        if hasattr(bundle, "model_dump_json"):
            bundle_json = bundle.model_dump_json(exclude_none=True, serialize_as_any=True)
            evidence_hash = getattr(bundle, "evidence_hash", "")
            timestamp = str(getattr(bundle, "timestamp", ""))
            algorithm = getattr(bundle, "algorithm", "") or getattr(bundle, "method_id", "")
            dataset = getattr(bundle, "dataset", "")
            bundle_dict = bundle.model_dump()
        elif isinstance(bundle, dict):
            bundle_json = json.dumps(bundle, default=str)
            evidence_hash = bundle.get("evidence_hash", "")
            timestamp = str(bundle.get("timestamp", ""))
            algorithm = bundle.get("algorithm", "") or bundle.get("method_id", "")
            dataset = bundle.get("dataset", "")
            bundle_dict = bundle
        else:
            raise TypeError("Bundle must be an EvidenceBundle instance or dict")

        existing_json = self._get_bundle_json(evidence_hash)
        if existing_json is not None:
            existing_dict = json.loads(existing_json)
            new_dict = json.loads(bundle_json)
            if existing_dict == new_dict:
                return evidence_hash
            else:
                raise EvidenceAlreadyRegisteredError(
                    f"Evidence hash {evidence_hash} already registered with DIFFERENT content. "
                    f"This indicates either a collision or attempted tampering. "
                    f"Use update_bundle() with explicit version bump to revise evidence."
                )

        cursor = self.conn.execute(
            "INSERT OR IGNORE INTO bundles VALUES (?, ?, ?, ?, ?)",
            (evidence_hash, bundle_json, timestamp, algorithm, dataset)
        )
        self.conn.commit()

        if cursor.rowcount == 0:
            return self.register(bundle)
        return evidence_hash

    def update_bundle(self, bundle: EvidenceBundle, reason: str) -> str:
        """Explicitly update an existing bundle with version increment (append-only)."""
        if not bundle.supersedes:
            raise ValueError("update_bundle requires bundle.supersedes to be set to the original hash")
        if not reason:
            raise ValueError("update_bundle requires a reason")

        bundle.update_reason = reason
        bundle.update_timestamp = datetime.now(timezone.utc).isoformat()
        payload = f"{bundle.supersedes}:{reason}:{bundle.update_timestamp}:{bundle.statistical_agreement}"
        bundle.evidence_hash = hashlib.sha256(payload.encode()).hexdigest()
        return self.register(bundle)

    def retrieve(self, evidence_hash: str) -> Optional[EvidenceBundle]:
        bundle_json = self._get_bundle_json(evidence_hash)
        if bundle_json:
            return EvidenceBundle(**json.loads(bundle_json))
        return None

    def list_bundles(self, algorithm: Optional[str] = None, dataset: Optional[str] = None) -> List[Dict[str, Any]]:
        query = "SELECT evidence_hash, algorithm, dataset FROM bundles"
        params = []
        conditions = []
        if algorithm:
            conditions.append("algorithm=?")
            params.append(algorithm)
        if dataset:
            conditions.append("dataset=?")
            params.append(dataset)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        cur = self.conn.execute(query, params)
        return [{"hash": r[0], "algorithm": r[1], "dataset": r[2]} for r in cur.fetchall()]
