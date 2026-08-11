#!/usr/bin/env python3
"""Verify VIREON × MOABB integration is complete."""
import subprocess, sys, os
from pathlib import Path

ROOT = Path(__file__).parent.parent
os.chdir(ROOT)
os.environ.setdefault("MNE_DATA", "/home/z/mne_data")
os.environ["MPLBACKEND"] = "Agg"

def run(cmd, timeout=120):
    env = {**os.environ, "PYTHONPATH": ".:vireon-core:vireon-moabb:vireon-evidence:vireon-knowledge:vireon-methods:vireon-validation:vireon-corpus:vireon-models:vireon-lab:vireon-api:vireon-verification"}
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, env=env)
        return r.returncode == 0, r.stdout + r.stderr
    except subprocess.TimeoutExpired:
        return False, "[TIMEOUT]"

def check(name, cmd, expected=None):
    success, output = run(cmd)
    if expected:
        success = success and expected in output
    print(f"  {'✓' if success else '✗'} {name}")
    if not success:
        print(f"    {output[-300:]}")
    return success

print("=" * 60)
print("VIREON × MOABB INTEGRATION VERIFICATION")
print("=" * 60)

results = {}

# 1. POC reproduces
print("\n1. POC Reproducibility")
results["poc"] = check("POC reproduces evidence",
    '''python3 -c "
import sys; sys.path.insert(0, 'vireon-moabb')
from vireon_moabb import MoabbExecutor, EvidenceAssembler
from vireon_moabb.spec import standard_spec
spec = standard_spec(dataset='BNCI2014_001', subject=1, pipeline_name='logvar_lda')
trace = MoabbExecutor(seed=42).run(spec)
bundle = EvidenceAssembler().assemble(spec.model_dump(), trace, None)
print(f'HASH:{bundle.evidence_hash[:16]}')
print(f'ACC:{trace.mean_accuracy:.4f}')
"''', "ACC:0.749")

# 2. Adapters exist
print("\n2. Adapters")
results["adapters"] = check("MOABB adapter",
    "python3 -c \"from vireon_moabb import MoabbExecutor; print('OK')\"", "OK")
results["mne_adapter"] = check("MNE adapter",
    "python3 -c \"from vireon_moabb.adapters import MneAdapter; print('OK')\"", "OK")
results["sklearn_adapter"] = check("sklearn adapter",
    "python3 -c \"from vireon_moabb.adapters import SklearnAdapter; print('OK')\"", "OK")

# 3. Robustness
print("\n3. Robustness")
results["robustness"] = check("perturbation engine",
    "python3 -c \"from vireon_moabb.robustness import PerturbationEngine; print('OK')\"", "OK")

# 4. Statistics
print("\n4. Statistics")
results["subject_level_ci"] = check("subject-level CI",
    "python3 -c \"from vireon_moabb.statistics import SubjectLevelBootstrap; print('OK')\"", "OK")

# 5. Evidence
print("\n5. Evidence")
results["evidence_bundle"] = check("evidence bundle",
    "python3 -c \"from vireon_moabb.evidence import EvidenceAssembler; print('OK')\"", "OK")

# 6. Reporting
print("\n6. Reporting")
results["raw_report"] = check("raw evidence report",
    "python3 -c \"from vireon_moabb.report import Reporter; r = Reporter(); assert hasattr(r, 'generate_raw_evidence_report'); print('OK')\"", "OK")

# 7. CLI
print("\n7. CLI")
results["cli"] = check("vireon validate command",
    "python3 -m vireon_lab.cli.main validate --help 2>&1 | head -3", "validate")

# 8. Native code deprecated
print("\n8. Deprecation")
results["deprecated"] = check("native algorithms deprecated",
    "test -d vireon-methods/reference/deprecated && echo 'DEPRECATED' || echo 'NOT_FOUND'", "DEPRECATED")

# Summary
passed = sum(results.values())
total = len(results)
print(f"\n{'='*60}")
print(f"RESULT: {passed}/{total} checks passed")
print(f"{'='*60}")
sys.exit(0 if passed == total else 1)
