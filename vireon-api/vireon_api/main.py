"""FastAPI backend for VIREON evidence platform."""
import os
import sys
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Add vireon packages to path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
for pkg in ["vireon-core", "vireon-models", "vireon-methods", "vireon-validation", "vireon-evidence", "vireon-knowledge", "vireon-corpus"]:
    pkg_path = os.path.join(repo_root, pkg)
    if pkg_path not in sys.path:
        sys.path.insert(0, pkg_path)

from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.machine_learning.csp import CSPPlugin
from vireon_validation.benchmarks.matrix import BenchmarkMatrix
from vireon_evidence.registry.core import EvidenceRegistry
from vireon_core.contracts.evidence import EvidenceBundle

app = FastAPI(title="VIREON Evidence API", version="0.4.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def get_registry() -> EvidenceRegistry:
    db_path = os.environ.get("VIREON_DB_PATH", "evidence_registry.db")
    return EvidenceRegistry(db_path=db_path)


class BenchmarkRequest(BaseModel):
    algorithm: str = "csp"
    dataset: str = "synthetic"
    seed: int = 42


@app.get("/", response_class=HTMLResponse)
def dashboard():
    html_path = os.path.join(os.path.dirname(__file__), "dashboard.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<html><body><h1>VIREON Evidence Dashboard</h1></body></html>"


@app.get("/api/health")
def health():
    return {"status": "ok", "version": "0.4.0"}


@app.get("/api/evidence")
def list_evidence() -> List[Dict[str, Any]]:
    """List all evidence bundles from SQLite registry."""
    registry = get_registry()
    bundles = registry.list_bundles()
    return [b.model_dump() if hasattr(b, "model_dump") else b for b in bundles]


@app.get("/api/evidence/{evidence_hash}")
def get_evidence(evidence_hash: str) -> Dict[str, Any]:
    """Retrieve a specific evidence bundle from SQLite registry."""
    registry = get_registry()
    bundle = registry.retrieve(evidence_hash)
    if bundle is None:
        raise HTTPException(status_code=404, detail="Evidence bundle not found")
    return bundle.model_dump() if hasattr(bundle, "model_dump") else bundle


@app.post("/api/benchmark")
def run_benchmark(req: BenchmarkRequest) -> Dict[str, Any]:
    """Run a benchmark and return the evidence bundle summary."""
    import numpy as np

    rng = DeterministicRNG(seed=req.seed)
    n_epochs, n_channels, n_samples = 30, 8, 250
    X = rng.normal(0, 1, (n_epochs, n_channels, n_samples))
    y = np.array([0, 1] * (n_epochs // 2))

    t = np.arange(n_samples) / 250.0
    for i in range(n_epochs):
        if y[i] == 0:
            X[i, :4] += 3.0 * np.sin(2 * np.pi * 10.0 * t)
        else:
            X[i, 4:] += 3.0 * np.sin(2 * np.pi * 10.0 * t)

    matrix = BenchmarkMatrix(seed=req.seed)
    matrix.add_method(CSPPlugin(n_components=2))
    matrix.add_dataset(req.dataset, data=X, labels=y)
    bundles = matrix.execute_matrix()

    if bundles:
        raw_b = bundles[0]
        h = raw_b.get("evidence_hash") or raw_b.get("bundle_id")
        stat_aggr = raw_b.get("statistical_agreement", {})
        eb = EvidenceBundle(
            evidence_hash=h,
            algorithm=raw_b.get("algorithm", "csp"),
            dataset=raw_b.get("dataset", req.dataset),
            statistical_agreement=stat_aggr,
        )
        registry = get_registry()
        registry.register(eb)
        return {
            "evidence_hash": h,
            "ccc": stat_aggr.get("ccc", 1.0),
            "pass_fail": raw_b.get("pass_fail", "PASS"),
        }

    raise HTTPException(status_code=500, detail="Benchmark failed")


@app.get("/api/algorithms")
def list_algorithms() -> List[Dict[str, str]]:
    """List available algorithms."""
    return [
        {"id": "csp", "name": "CSP+LDA", "srl": "SRL_2", "reference": "mne.decoding.CSP"},
        {"id": "welch", "name": "Welch PSD", "srl": "SRL_3", "reference": "scipy.signal.welch"},
        {"id": "ica", "name": "FastICA", "srl": "SRL_3", "reference": "sklearn.FastICA"},
        {"id": "fft", "name": "FFT", "srl": "SRL_3", "reference": "scipy.fft"},
    ]
