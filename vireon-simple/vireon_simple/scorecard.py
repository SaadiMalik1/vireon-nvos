from dataclasses import dataclass
from typing import Literal

@dataclass
class ScorecardDimension:
    name: str
    score: int
    max: int
    explanation: str

@dataclass
class Scorecard:
    dimensions: list[ScorecardDimension]
    total: int  # 0-100
    confidence: Literal["LOW", "MEDIUM", "HIGH"]
    
    @classmethod
    def from_result(cls, result: "ExperimentResult") -> "Scorecard":
        dims = []
        
        # Correctness
        ccc = result.statistics.get("ccc", 0)
        if ccc >= 0.99: score, expl = 20, "Numerical implementation matches reference (CCC ≥ 0.99)"
        elif ccc >= 0.95: score, expl = 15, "Numerical implementation closely matches reference (CCC ≥ 0.95)"
        elif ccc >= 0.90: score, expl = 10, "Numerical implementation approximately matches reference (CCC ≥ 0.90)"
        else: score, expl = 5, "Numerical implementation diverges from reference (CCC < 0.90)"
        dims.append(ScorecardDimension("Correctness", score, 20, expl))
        
        # Statistics
        has_cv = result.validation.strategy != "single_run"
        has_sig = result.spec.statistics.significance_test is not None
        has_ci = result.spec.statistics.confidence_interval is not None
        stat_score = sum([has_cv * 7, has_sig * 7, has_ci * 6])
        dims.append(ScorecardDimension("Statistics", stat_score, 20, 
            f"CV: {'✓' if has_cv else '✗'}, Significance: {'✓' if has_sig else '✗'}, CI: {'✓' if has_ci else '✗'}"))
        
        # Reproducibility
        if getattr(result.provenance, "reproducibility_verified", False):
            repro_score = 20
            repro_expl = "Same seed produces identical results"
        else:
            repro_score = 0
            repro_expl = "Reproducibility not verified"
        dims.append(ScorecardDimension("Reproducibility", repro_score, 20, repro_expl))
        
        # Robustness
        n_perturbations = len(result.robustness.perturbations) if result.robustness else 0
        if n_perturbations >= 3: rob_score, rob_expl = 20, f"Tested with {n_perturbations} perturbation types"
        elif n_perturbations >= 1: rob_score, rob_expl = 12, f"Tested with {n_perturbations} perturbation type(s)"
        else: rob_score, rob_expl = 0, "No robustness testing"
        dims.append(ScorecardDimension("Robustness", rob_score, 20, rob_expl))
        
        # Data quality
        quality = result.dataset_quality
        if quality.missing_pct < 0.1 and quality.clipping_pct < 1 and not quality.dc_drift:
            dq_score, dq_expl = 20, "Clean data"
        elif quality.missing_pct < 1 and quality.clipping_pct < 5:
            dq_score, dq_expl = 12, f"Minor issues: {quality.missing_pct}% missing, {quality.clipping_pct}% clipping"
        else:
            dq_score, dq_expl = 4, f"Severe issues: {quality.missing_pct}% missing, {quality.clipping_pct}% clipping"
        dims.append(ScorecardDimension("Data quality", dq_score, 20, dq_expl))
        
        # Leakage
        if getattr(result.validation, "leakage_verified", False):
            leak_score, leak_expl = 20, "Train/test isolation verified"
        else:
            leak_score, leak_expl = 0, "Leakage check not performed or suspected"
        dims.append(ScorecardDimension("Leakage", leak_score, 20, leak_expl))
        
        total = sum(d.score for d in dims) * 100 // 120
        if total >= 80: confidence = "HIGH"
        elif total >= 60: confidence = "MEDIUM"
        else: confidence = "LOW"
        
        return cls(dims, total, confidence)
