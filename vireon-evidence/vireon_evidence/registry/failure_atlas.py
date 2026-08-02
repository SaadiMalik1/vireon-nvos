import sqlite3
import json
import hashlib
from typing import Dict, Any, List, Union

class FailureAtlas:
    """
    Registry for cataloging algorithm failures, preserving them as scientific evidence 
    rather than discarding them. Persisted via SQLite.
    """
    def __init__(self, db_path: str = "failure_atlas.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS failures (
                hash TEXT PRIMARY KEY,
                timestamp TEXT,
                method_id TEXT,
                dataset_id TEXT,
                failure_record JSON
            )
        """)
        self.conn.commit()

    def register_failure(self, failure: Union[dict, str] = None, *args, **kwargs) -> str:
        if isinstance(failure, dict):
            failure_record = failure.copy()
        else:
            if failure is not None:
                algorithm = failure
                dataset = args[0] if len(args) > 0 else kwargs.get("dataset", "")
                perturbation = args[1] if len(args) > 1 else kwargs.get("perturbation", "")
                severity = args[2] if len(args) > 2 else kwargs.get("severity", 0.0)
                assumption_violated = args[3] if len(args) > 3 else kwargs.get("assumption_violated", "")
                error_metrics = args[4] if len(args) > 4 else kwargs.get("error_metrics", {})
                failure_mechanism = args[5] if len(args) > 5 else kwargs.get("failure_mechanism", "")
            else:
                algorithm = kwargs.get("algorithm", "")
                dataset = kwargs.get("dataset", "")
                perturbation = kwargs.get("perturbation", "")
                severity = kwargs.get("severity", 0.0)
                assumption_violated = kwargs.get("assumption_violated", "")
                error_metrics = kwargs.get("error_metrics", {})
                failure_mechanism = kwargs.get("failure_mechanism", "")

            failure_record = {
                "algorithm": algorithm,
                "dataset": dataset,
                "perturbation": perturbation,
                "severity": severity,
                "assumption_violated": assumption_violated,
                "error_metrics": error_metrics,
                "failure_mechanism": failure_mechanism,
                "method_id": algorithm,
                "dataset_id": dataset
            }

        h = hashlib.sha256(json.dumps(failure_record, sort_keys=True).encode()).hexdigest()
        failure_record["reproducibility_hash"] = h
        
        method_id = failure_record.get("method_id") or failure_record.get("algorithm")
        dataset_id = failure_record.get("dataset_id") or failure_record.get("dataset")
        timestamp = failure_record.get("timestamp")

        self.conn.execute(
            "INSERT OR REPLACE INTO failures VALUES (?, ?, ?, ?, ?)",
            (h, timestamp, method_id, dataset_id, json.dumps(failure_record))
        )
        self.conn.commit()
        return h

    def get_failure(self, hash: str) -> dict:
        cur = self.conn.execute("SELECT failure_record FROM failures WHERE hash=?", (hash,))
        row = cur.fetchone()
        return json.loads(row[0]) if row else None

    def list_failures(self, method_id: str = None) -> list:
        if method_id:
            cur = self.conn.execute("SELECT failure_record FROM failures WHERE method_id=?", (method_id,))
        else:
            cur = self.conn.execute("SELECT failure_record FROM failures")
        return [json.loads(row[0]) for row in cur.fetchall()]

    def query_failures(self, algorithm: str = None, dataset: str = None) -> List[Dict[str, Any]]:
        failures = self.list_failures()
        if algorithm:
            failures = [f for f in failures if f.get("algorithm") == algorithm or f.get("method_id") == algorithm]
        if dataset:
            failures = [f for f in failures if f.get("dataset") == dataset or f.get("dataset_id") == dataset]
        return failures
