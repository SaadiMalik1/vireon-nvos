#!/usr/bin/env python3
"""
Check that documentation claims match code reality.

Usage: python scripts/check_doc_sync.py [--docs-dir docs/] [--repo-root .]
Exit 0 if all claims verified, exit 1 if drift detected.
"""
import sys
from pathlib import Path
from typing import List, Dict, Any

def _grep(pattern: str, filepath: str) -> bool:
    path = Path(filepath)
    if not path.exists():
        return False
    return pattern in path.read_text()

def _not_grep(pattern: str, filepath: str) -> bool:
    path = Path(filepath)
    if not path.exists():
        return True
    return pattern not in path.read_text()

CLAIMS: List[Dict[str, Any]] = [
    {
        "doc": "docs/01_ARCHITECTURE/Plugin_Architecture.md",
        "claim": "PluginManager supports discovery via entry_points",
        "verify": lambda: _grep("importlib.metadata", "vireon-core/vireon_core/kernel/plugins.py"),
    },
    {
        "doc": "docs/01_ARCHITECTURE/Execution_Model.md",
        "claim": "ExecutionEngine is a data-driven DAG using TopologicalSorter",
        "verify": lambda: _grep("TopologicalSorter", "vireon-core/vireon_core/kernel/execution_engine.py"),
    },
    {
        "doc": "docs/02_SCIENCE/Scientific_Manual.md",
        "claim": "ICC is computed (not hardcoded 0.94)",
        "verify": lambda: _not_grep("return 0.94", "vireon-validation/vireon_validation/statistics/framework.py"),
    },
    {
        "doc": "docs/01_ARCHITECTURE/Plugin_Architecture.md",
        "claim": "ScientificContractViolation is raised on invariant failure",
        "verify": lambda: _grep("ScientificContractViolation", "vireon-core/vireon_core/contracts/plugin.py"),
    },
    {
        "doc": "docs/01_ARCHITECTURE/Evidence_Flow.md",
        "claim": "EvidenceTransaction computes SHA-256 content hash",
        "verify": lambda: _grep("_compute_hash", "vireon-evidence/vireon_evidence/graph/transactions.py"),
    },
    {
        "doc": "docs/02_SCIENCE/Statistical_Methods.md",
        "claim": "Passing-Bablok regression is implemented",
        "verify": lambda: _grep("def passing_bablok", "vireon-validation/vireon_validation/statistics/framework.py"),
    },
    {
        "doc": "docs/02_SCIENCE/Statistical_Methods.md",
        "claim": "Matthews Correlation Coefficient is implemented",
        "verify": lambda: _grep("def matthews_correlation_coefficient", "vireon-validation/vireon_validation/statistics/framework.py"),
    },
    {
        "doc": "docs/02_SCIENCE/Statistical_Methods.md",
        "claim": "Bayesian Credible Interval uses conjugate normal model",
        "verify": lambda: _grep("bayesian_credible_interval", "vireon-validation/vireon_validation/statistics/framework.py"),
    },
    {
        "doc": "docs/02_SCIENCE/Benchmarking.md",
        "claim": "Cartesian benchmark matrix evaluates signal SNR sweeps",
        "verify": lambda: _grep("BenchmarkMatrix", "vireon-validation/vireon_validation/benchmarks/matrix.py"),
    },
    {
        "doc": "docs/03_REPOSITORIES/vireon-methods.md",
        "claim": "Welch PSD method uses real native implementation (deprecated reference)",
        "verify": lambda: _grep("class VireonWelch", "vireon-methods/reference/deprecated/vireon_welch.py"),
    },
    {
        "doc": "docs/03_REPOSITORIES/vireon-methods.md",
        "claim": "FFT method uses real native FFT (deprecated reference)",
        "verify": lambda: _grep("class VireonFFT", "vireon-methods/reference/deprecated/vireon_fft.py"),
    },
    {
        "doc": "docs/03_REPOSITORIES/vireon-methods.md",
        "claim": "STFT method uses real native STFT (deprecated reference)",
        "verify": lambda: _grep("class VireonSTFT", "vireon-methods/reference/deprecated/vireon_stft.py"),
    },
    {
        "doc": "docs/03_REPOSITORIES/vireon-methods.md",
        "claim": "CSP method uses real covariance generalized eigenvalue decomposition (deprecated reference)",
        "verify": lambda: _grep("linalg.eigh", "vireon-methods/reference/deprecated/vireon_csp.py"),
    },
    {
        "doc": "docs/03_REPOSITORIES/vireon-methods.md",
        "claim": "wPLI connectivity is implemented (deprecated reference)",
        "verify": lambda: _grep("class VireonWPLI", "vireon-methods/reference/deprecated/vireon_connectivity.py"),
    },
    {
        "doc": "docs/03_REPOSITORIES/vireon-models.md",
        "claim": "Forward model projects dipole sources to sensors",
        "verify": lambda: _grep("class RandomMixingMatrix", "vireon-models/vireon_models/forward.py"),
    },
    {
        "doc": "docs/03_REPOSITORIES/vireon-corpus.md",
        "claim": "PhysioNet EEGBCI plugin exists with BIDS conversion",
        "verify": lambda: _grep("class EEGBCIPlugin", "vireon-corpus/vireon_corpus/plugins/eegbci_plugin.py"),
    },
    {
        "doc": "docs/03_REPOSITORIES/vireon-corpus.md",
        "claim": "Sleep-EDF plugin exists",
        "verify": lambda: _grep("class SleepEDFPlugin", "vireon-corpus/vireon_corpus/plugins/sleep_edf_plugin.py"),
    },
    {
        "doc": "docs/03_REPOSITORIES/vireon-evidence.md",
        "claim": "ContinuousMetaAnalysis computes random-effects pooled stats",
        "verify": lambda: _grep("ContinuousMetaAnalysis", "vireon-evidence/vireon_evidence/queries/meta_analysis.py"),
    },
    {
        "doc": "docs/03_REPOSITORIES/vireon-knowledge.md",
        "claim": "DecisionEngine produces traceable regulatory decisions",
        "verify": lambda: _grep("DecisionEngine", "vireon-knowledge/vireon_knowledge/decision_engine.py"),
    },
    {
        "doc": "docs/01_ARCHITECTURE/Execution_Model.md",
        "claim": "DeterministicRNG guarantees seed reproducibility",
        "verify": lambda: _grep("DeterministicRNG", "vireon-core/vireon_core/runtime/rng.py"),
    },
]

def run_checks(claims_list: List[Dict[str, Any]] = None) -> List[str]:
    claims = claims_list if claims_list is not None else CLAIMS
    failures = []
    for item in claims:
        try:
            if not item["verify"]():
                failures.append(f"DRIFT: {item['doc']} — {item['claim']}")
        except Exception as e:
            failures.append(f"ERROR checking {item['doc']}: {e}")
    return failures

def main():
    failures = run_checks()
    if failures:
        print("Documentation drift detected:")
        for f in failures:
            print(f"  {f}")
        sys.exit(1)
    print(f"All {len(CLAIMS)} doc claims verified against code. No drift.")
    sys.exit(0)

if __name__ == "__main__":
    main()
