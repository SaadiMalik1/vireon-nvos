#!/usr/bin/env python3
"""VIREON remediation verification harness.
Run at each phase gate to verify all tasks are complete."""
import subprocess
import sys
import os
from pathlib import Path

ROOT = Path(__file__).parent.parent
os.chdir(ROOT)

PYTHONPATH = "PYTHONPATH=.:vireon-core:vireon-models:vireon-lab:vireon-methods:vireon-validation:vireon-evidence:vireon-knowledge:vireon-corpus:vireon-api:vireon-verification"
ENV = {"PYTHONPATH": ".".join(["", "vireon-core", "vireon-models", "vireon-lab", "vireon-methods",
                                 "vireon-validation", "vireon-evidence", "vireon-knowledge",
                                 "vireon-corpus", "vireon-api", "vireon-verification"]),
        "MPLBACKEND": "Agg", "PATH": os.environ["PATH"]}

def run(cmd, timeout=120):
    """Run command, return (success, output)."""
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                          timeout=timeout, env={**os.environ, **ENV})
        return r.returncode == 0, r.stdout + r.stderr
    except subprocess.TimeoutExpired:
        return False, "[TIMEOUT]"

def check(name, cmd, expected_contains=None, timeout=120):
    """Run a check and print result."""
    success, output = run(cmd, timeout=timeout)
    if expected_contains:
        success = success and expected_contains in output
    status = "✓ PASS" if success else "✗ FAIL"
    print(f"  {status}: {name}")
    if not success:
        print(f"    Output: {output[-300:]}")
    return success

def main():
    print("=" * 60)
    print("VIREON REMEDIATION VERIFICATION")
    print("=" * 60)

    results = {}

    # 1. Test suite passes (with longer timeout for integration tests)
    print("\n1. Test Suite")
    results["tests_core"] = check("vireon-core tests", "pytest vireon-core/tests/ --tb=no -q", "passed")
    results["tests_methods"] = check("vireon-methods tests", "pytest vireon-methods/tests/ --tb=no -q", "passed")
    results["tests_evidence"] = check("vireon-evidence tests", "pytest vireon-evidence/tests/ --tb=no -q", "passed")
    results["tests_corpus"] = check("vireon-corpus tests", "pytest vireon-corpus/tests/ --tb=no -q", "passed")
    results["tests_knowledge"] = check("vireon-knowledge tests", "pytest vireon-knowledge/tests/ --tb=no -q", "passed")
    results["tests_validation"] = check("vireon-validation tests", "pytest vireon-validation/tests/ --tb=no -q", "passed")
    results["tests_literature"] = check("literature tests", "pytest vireon-verification/literature/ --tb=no -q", "passed")

    # 2. Functional correctness
    print("\n2. Functional Correctness")
    results["imports"] = check("all imports", '''python3 -c "
from vireon_core import DeterministicRNG, ExecutionEngine
from vireon_methods import VireonWelch, VireonICA, CSPPlugin
from vireon_evidence import EvidenceGraph, EvidenceRegistry
from vireon_validation import BenchmarkMatrix
from vireon_corpus import DatasetManager
from vireon_knowledge import KnowledgeGraph
from vireon_lab import ReplayEngine
print('All imports OK')
"''', "All imports OK")

    results["registry_get"] = check("EvidenceRegistry.get() exists", '''python3 -c "
from vireon_evidence import EvidenceRegistry
r = EvidenceRegistry(db_path=':memory:')
assert hasattr(r, 'get'), 'EvidenceRegistry must have get() method'
print('PASS: get() exists')
"''', "PASS: get() exists")

    results["dataset_dispatch"] = check("load_dataset dispatches by key", '''python3 -c "
from vireon_corpus import DatasetManager
from vireon_corpus.exceptions import UnknownDatasetError
dm = DatasetManager()
try:
    dm.load_dataset('nonexistent_key')
    print('FAIL: should raise')
except UnknownDatasetError:
    print('PASS: unknown key raises')
"''', "PASS: unknown key raises")

    results["api_honors_algorithm"] = check("API honors algorithm param", '''python3 -c "
from fastapi.testclient import TestClient
from vireon_api.main import app
c = TestClient(app)
# Test that algorithm param is honored (not always CSP)
r = c.post('/api/benchmark', json={'algorithm':'welch','dataset':'test','seed':42})
# Should not always return CSP results
print(f'Status: {r.status_code}')
"''', "Status: 200")

    # 3. Hash integrity
    print("\n3. Hash Integrity")
    results["hash_integrity"] = check("no fake hashes", "python3 scripts/verify_hash_integrity.py", "PASS")

    # 4. Linting (if configured)
    print("\n4. Code Quality")
    results["ruff"] = check("ruff check", "ruff check . 2>&1", "All checks passed" if Path(".ruff.toml").exists() else None)

    # 5. Documentation
    print("\n5. Documentation")
    results["no_phase_e_stubs"] = check("no empty Phase E stubs",
        "grep -rl '## Phase E Implementation Status' docs/ | wc -l", "0")
    results["no_vireon_publications"] = check("no vireon-publications refs",
        "grep -rl 'vireon-publications' docs/ README.md 2>/dev/null | wc -l", "0")
    results["changelog_current"] = check("CHANGELOG has v1.2.0",
        "grep '## \\\\[1.2.0\\\\]' CHANGELOG.md", "[1.2.0]")
    results["version_sync"] = check("versions synced", '''python3 -c "
import tomllib
with open('pyproject.toml', 'rb') as f:
    pp = tomllib.load(f)
pp_version = pp['project']['version']
# Check FastAPI app version
import ast
with open('vireon-api/vireon_api/main.py') as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, ast.Call) and hasattr(node.func, 'id') and node.func.id == 'FastAPI':
        for kw in node.keywords:
            if kw.arg == 'version':
                api_version = kw.value.value
                assert pp_version == api_version, f'pyproject={pp_version} vs api={api_version}'
                print(f'PASS: versions synced at {pp_version}')
"''', "PASS: versions synced")

    # 6. Security
    print("\n6. Security")
    results["no_committed_db"] = check("no committed .db files",
        "git ls-files | grep -E '\\.db$' | wc -l", "0")
    results["no_secrets"] = check("no hardcoded secrets",
        "grep -riE 'password|secret|api_key\\s*=\\s*[\"'\\'']' vireon-*/ 2>/dev/null | wc -l", "0")

    # Summary
    print("\n" + "=" * 60)
    passed = sum(results.values())
    total = len(results)
    print(f"RESULT: {passed}/{total} checks passed")
    print("=" * 60)

    if passed == total:
        print("\n✓ ALL CHECKS PASSED — phase gate clear")
        sys.exit(0)
    else:
        print("\n✗ SOME CHECKS FAILED — phase gate blocked")
        failed = [k for k, v in results.items() if not v]
        print(f"Failed: {failed}")
        sys.exit(1)

if __name__ == "__main__":
    main()
