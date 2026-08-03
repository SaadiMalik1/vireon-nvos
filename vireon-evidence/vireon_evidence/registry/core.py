import sqlite3
import json
from typing import Optional, List, Dict, Any
from vireon_core.contracts.evidence import EvidenceBundle


class EvidenceRegistry:
    """
    Evidence Registry with SQLite backend for persisting and querying evidence bundles.
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

    def register(self, bundle: Any):
        if hasattr(bundle, "model_dump_json"):
            bundle_json = bundle.model_dump_json()
            evidence_hash = getattr(bundle, "evidence_hash", "")
            timestamp = str(getattr(bundle, "timestamp", ""))
            algorithm = getattr(bundle, "algorithm", "") or getattr(bundle, "method_id", "")
            dataset = getattr(bundle, "dataset", "")
        elif isinstance(bundle, dict):
            bundle_json = json.dumps(bundle, default=str)
            evidence_hash = bundle.get("evidence_hash", "")
            timestamp = str(bundle.get("timestamp", ""))
            algorithm = bundle.get("algorithm", "") or bundle.get("method_id", "")
            dataset = bundle.get("dataset", "")
        else:
            raise TypeError("Bundle must be an EvidenceBundle instance or dict")

        self.conn.execute(
            "INSERT OR REPLACE INTO bundles VALUES (?, ?, ?, ?, ?)",
            (evidence_hash, bundle_json, timestamp, algorithm, dataset)
        )
        self.conn.commit()

    def retrieve(self, evidence_hash: str) -> Optional[EvidenceBundle]:
        cur = self.conn.execute("SELECT bundle FROM bundles WHERE evidence_hash=?", (evidence_hash,))
        row = cur.fetchone()
        if row:
            return EvidenceBundle(**json.loads(row[0]))
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
