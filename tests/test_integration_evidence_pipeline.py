"""Integration test: the flagship demo produces real cryptographic evidence.

This is the single most important test in the repository. If it fails, VIREON
is not a research prototype.
"""
import json
import os
import subprocess
import sys
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEMO_PATH = os.path.join(REPO_ROOT, "examples", "first_validation", "demo.py")
OUTPUT_PATH = os.path.join(REPO_ROOT, "output", "evidence.json")

def test_demo_produces_non_empty_evidence_hash():
    """The demo's evidence bundle must have a non-empty cryptographic hash."""
    _run_demo()
    bundle = _load_evidence()
    assert bundle["evidence_hash"] != "", "evidence_hash is empty — pipeline broken"
    assert len(bundle["evidence_hash"]) == 64, "evidence_hash must be 64-char hex"
    int(bundle["evidence_hash"], 16)  # valid hex

def test_demo_produces_real_ccc():
    """CCC must be computed (not 0.0, not 0.95 hardcoded)."""
    _run_demo()
    bundle = _load_evidence()
    ccc = bundle["statistical_agreement"]["ccc"]
    assert ccc > 0.0, f"CCC is {ccc} — no real computation happened"
    assert ccc != 0.95, "CCC is hardcoded 0.95"

def test_demo_pass_fail_matches_conclusion_verdict():
    """pass_fail and conclusion_verdict must agree."""
    _run_demo()
    bundle = _load_evidence()
    assert bundle["pass_fail"] == bundle["conclusion_verdict"], \
        f"pass_fail={bundle['pass_fail']} != conclusion_verdict={bundle['conclusion_verdict']}"

def test_demo_baseline_verdict_is_pass():
    """The baseline (unperturbed) bundle should achieve PASS."""
    _run_demo()
    bundle = _load_evidence()
    assert bundle["conclusion_verdict"] == "PASS", \
        f"Baseline verdict is {bundle['conclusion_verdict']} — pipeline not producing real evidence"

def test_demo_populates_algorithm_field():
    """algorithm field must be populated."""
    _run_demo()
    bundle = _load_evidence()
    assert bundle["algorithm"] != "", "algorithm field is empty"

def test_demo_measures_runtime():
    """runtime_sec must be a real measured value."""
    _run_demo()
    bundle = _load_evidence()
    assert bundle["runtime_sec"] > 0.0, "runtime_sec is 0 — not measured"

def test_demo_deterministic_replay():
    """Running the demo twice with the same seed must produce the same evidence_hash."""
    _run_demo()
    with open(OUTPUT_PATH) as f:
        hash1 = json.load(f)["evidence_hash"]
    
    _run_demo()
    with open(OUTPUT_PATH) as f:
        hash2 = json.load(f)["evidence_hash"]
    
    assert hash1 == hash2, f"Non-deterministic: {hash1} != {hash2}"

def test_demo_different_seed_different_hash():
    """Different seeds should produce different hashes (proving the hash is meaningful)."""
    _run_demo(extra_env={"VIREON_SEED": "42"})
    with open(OUTPUT_PATH) as f:
        hash1 = json.load(f)["evidence_hash"]
    
    _run_demo(extra_env={"VIREON_SEED": "43"})
    with open(OUTPUT_PATH) as f:
        hash2 = json.load(f)["evidence_hash"]
        
    assert hash1 != hash2, "Different seeds produced same hash"

def _run_demo(extra_env=None):
    """Run the demo and ensure output/evidence.json exists."""
    env = os.environ.copy()
    env["PYTHONPATH"] = ":".join([
        REPO_ROOT,
        os.path.join(REPO_ROOT, "vireon-core"),
        os.path.join(REPO_ROOT, "vireon-models"),
        os.path.join(REPO_ROOT, "vireon-methods"),
        os.path.join(REPO_ROOT, "vireon-validation"),
        os.path.join(REPO_ROOT, "vireon-evidence"),
        os.path.join(REPO_ROOT, "vireon-knowledge"),
        os.path.join(REPO_ROOT, "vireon-corpus"),
    ])
    env["MPLBACKEND"] = "Agg"
    if extra_env:
        env.update(extra_env)
    result = subprocess.run(
        [sys.executable, DEMO_PATH],
        cwd=REPO_ROOT, env=env, capture_output=True, text=True, timeout=120
    )
    assert result.returncode == 0, f"Demo failed:\n{result.stderr}"
    assert os.path.exists(OUTPUT_PATH), "Demo did not produce output/evidence.json"

def _load_evidence():
    with open(OUTPUT_PATH) as f:
        return json.load(f)

