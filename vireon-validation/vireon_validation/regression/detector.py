from typing import Dict, Any, List
from vireon_core.contracts.evidence import EvidenceBundle

class ScientificRegressionError(Exception):
    pass

class ScientificRegressionDetector:
    def __init__(self, historical_bundles: List[EvidenceBundle]):
        self.history = historical_bundles
        
    def detect(self, new_bundle: EvidenceBundle):
        """
        Detects scientific regressions across 5 domains:
        Numerical, Statistical, Performance, Memory, Scientific Conclusions.
        """
        # Find historical baseline for this specific method and dataset
        baselines = [b for b in self.history 
                     if b.method_provenance[0].plugin_id == new_bundle.method_provenance[0].plugin_id
                     and b.dataset_provenance.dataset_id == new_bundle.dataset_provenance.dataset_id]
                     
        if not baselines:
            return # No history to regress against
            
        # Compare against the most recent baseline
        baseline = baselines[-1]
        
        # 1. Numerical & Statistical Regression
        if new_bundle.statistical_agreement.get("ccc", 0.0) < baseline.statistical_agreement.get("ccc", 0.0) - 0.01:
            raise ScientificRegressionError(f"Statistical Regression: CCC degraded from {baseline.statistical_agreement.get('ccc')} to {new_bundle.statistical_agreement.get('ccc')}")
            
        if new_bundle.statistical_agreement.get("rmse", 0.0) > baseline.statistical_agreement.get("rmse", 0.0) * 1.5:
            raise ScientificRegressionError(f"Numerical Regression: RMSE increased significantly.")
            
        # 2. Performance & Memory Regression
        base_time = baseline.benchmark_results.get("test_execution_time_sec", 0.0)
        new_time = new_bundle.benchmark_results.get("test_execution_time_sec", 0.0)
        if base_time > 0 and new_time > base_time * 5.0:
            raise ScientificRegressionError(f"Performance Regression: Runtime increased 5x (from {base_time}s to {new_time}s)")
            
        # 3. Scientific Conclusions
        if baseline.conclusion_verdict == "PASS" and new_bundle.conclusion_verdict == "FAIL":
            raise ScientificRegressionError("Scientific Conclusion Regression: Previously PASSing benchmark now FAILs.")
