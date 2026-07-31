import json
import hashlib
from typing import Dict, Any, List

class FailureAtlas:
    """
    Registry for cataloging algorithm failures, preserving them as scientific evidence 
    rather than discarding them.
    """
    def __init__(self, db_path: str = "failure_atlas.json"):
        self.db_path = db_path
        self.failures = []
        
    def register_failure(self, algorithm: str, dataset: str, perturbation: str, 
                         severity: float, assumption_violated: str, 
                         error_metrics: Dict[str, float], failure_mechanism: str) -> str:
        
        failure_record = {
            "algorithm": algorithm,
            "dataset": dataset,
            "perturbation": perturbation,
            "severity": severity,
            "assumption_violated": assumption_violated,
            "error_metrics": error_metrics,
            "failure_mechanism": failure_mechanism
        }
        
        # Create reproducibility hash
        record_str = json.dumps(failure_record, sort_keys=True).encode('utf-8')
        repro_hash = hashlib.sha256(record_str).hexdigest()
        failure_record["reproducibility_hash"] = repro_hash
        
        self.failures.append(failure_record)
        return repro_hash
        
    def query_failures(self, algorithm: str = None, dataset: str = None) -> List[Dict[str, Any]]:
        results = self.failures
        if algorithm:
            results = [f for f in results if f["algorithm"] == algorithm]
        if dataset:
            results = [f for f in results if f["dataset"] == dataset]
        return results
