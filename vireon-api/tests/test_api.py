import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient
from vireon_api.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["version"] == "1.1.0"


def test_api_key_auth(monkeypatch):
    monkeypatch.setenv("VIREON_API_KEY", "secret_key_123")
    # Request without key -> 401
    resp = client.get("/api/algorithms")
    assert resp.status_code == 401

    # Request with invalid key -> 401
    resp = client.get("/api/algorithms", headers={"X-API-Key": "wrong_key"})
    assert resp.status_code == 401

    # Request with valid key -> 200
    resp = client.get("/api/algorithms", headers={"X-API-Key": "secret_key_123"})
    assert resp.status_code == 200


def test_dashboard():
    response = client.get("/")
    assert response.status_code == 200
    assert "VIREON Evidence Dashboard" in response.text


def test_algorithms():
    response = client.get("/api/algorithms")
    assert response.status_code == 200
    algos = response.json()
    assert len(algos) >= 4
    ids = [a["id"] for a in algos]
    assert "csp" in ids
    assert "welch" in ids


def test_benchmark_and_retrieve_evidence():
    # Run benchmark
    bench_resp = client.post("/api/benchmark", json={"algorithm": "csp", "dataset": "synthetic", "seed": 42})
    assert bench_resp.status_code == 200
    data = bench_resp.json()
    assert "evidence_hash" in data
    assert "ccc" in data
    assert data["pass_fail"] == "PASS"

    # List evidence
    list_resp = client.get("/api/evidence")
    assert list_resp.status_code == 200
    evidence_list = list_resp.json()
    assert len(evidence_list) >= 1

    # Get specific evidence
    h = data["evidence_hash"]
    get_resp = client.get(f"/api/evidence/{h}")
    assert get_resp.status_code == 200
    bundle = get_resp.json()
    assert bundle["evidence_hash"] == h
