"""FastAPI backend for VIREON evidence platform."""
import os
import sys
import secrets
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader
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

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: Optional[str] = Security(API_KEY_HEADER)):
    """Verify API key. Skips verification if VIREON_API_KEY env var is not set."""
    expected_key = os.environ.get("VIREON_API_KEY")
    if not expected_key:
        return True
    if not api_key or not secrets.compare_digest(api_key, expected_key):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return True


app = FastAPI(title="VIREON Evidence API", version="1.1.0")

allowed_origins = os.environ.get("VIREON_CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


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
    return {"status": "ok", "version": "1.1.0"}


@app.get("/api/evidence")
def list_evidence(_: bool = Depends(verify_api_key)) -> List[Dict[str, Any]]:
    """List all evidence bundles from SQLite registry."""
    registry = get_registry()
    bundles = registry.list_bundles()
    return [b.model_dump() if hasattr(b, "model_dump") else b for b in bundles]


@app.get("/api/evidence/{evidence_hash}")
def get_evidence(evidence_hash: str, _: bool = Depends(verify_api_key)) -> Dict[str, Any]:
    """Retrieve a specific evidence bundle from SQLite registry."""
    registry = get_registry()
    bundle = registry.retrieve(evidence_hash)
    if bundle is None:
        raise HTTPException(status_code=404, detail="Evidence bundle not found")
    return bundle.model_dump() if hasattr(bundle, "model_dump") else bundle


@app.post("/api/benchmark")
def run_benchmark(req: BenchmarkRequest, _: bool = Depends(verify_api_key)) -> Dict[str, Any]:
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
        return {
            "evidence_hash": h,
            "ccc": stat_aggr.get("ccc", 1.0),
            "pass_fail": raw_b.get("pass_fail", "PASS"),
        }

    raise HTTPException(status_code=500, detail="Benchmark failed")


@app.get("/api/algorithms")
def list_algorithms(_: bool = Depends(verify_api_key)) -> List[Dict[str, str]]:
    """List available algorithms."""
    return [
        {"id": "csp", "name": "CSP+LDA", "srl": "SRL_2", "reference": "mne.decoding.CSP"},
        {"id": "welch", "name": "Welch PSD", "srl": "SRL_3", "reference": "scipy.signal.welch"},
        {"id": "ica", "name": "FastICA", "srl": "SRL_3", "reference": "sklearn.FastICA"},
        {"id": "fft", "name": "FFT", "srl": "SRL_3", "reference": "scipy.fft"},
    ]
