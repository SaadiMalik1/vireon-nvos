from hypothesis import given, strategies as st
import hashlib
import json


@given(
    algo=st.text(min_size=1, max_size=20),
    dataset=st.text(min_size=1, max_size=20),
    seed=st.integers(0, 10000),
    ccc=st.floats(0.0, 1.0, allow_nan=False),
)
def test_evidence_hash_determinism_and_uniqueness(algo, dataset, seed, ccc):
    """Evidence hash must be deterministic for identical payloads and unique for different seeds."""
    payload1 = {"algo": algo, "dataset": dataset, "seed": seed, "ccc": round(ccc, 6)}
    payload2 = {"algo": algo, "dataset": dataset, "seed": seed, "ccc": round(ccc, 6)}
    payload3 = {"algo": algo, "dataset": dataset, "seed": seed + 1, "ccc": round(ccc, 6)}

    h1 = hashlib.sha256(json.dumps(payload1, sort_keys=True).encode()).hexdigest()
    h2 = hashlib.sha256(json.dumps(payload2, sort_keys=True).encode()).hexdigest()
    h3 = hashlib.sha256(json.dumps(payload3, sort_keys=True).encode()).hexdigest()

    assert h1 == h2
    assert h1 != h3
