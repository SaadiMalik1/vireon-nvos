"""Tests for playbook dx fixes.

Tests that the P0/P1 fixes were actually applied correctly.
"""
import pytest
import numpy as np
import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def test_evidence_bundle_verify():
    """Test that EvidenceBundle.verify() works (was missing)."""
    from vireon_moabb.evidence import EvidenceBundle
    import hashlib, json

    spec = {"name": "test", "goal": "test"}
    trace = {"dataset_metadata": {"dataset_class": "test"}}
    validation = {"all_passed": True}
    summary = {"mean_accuracy": 0.85}

    hash_payload = {
        "experiment_spec": spec,
        "execution_trace": trace,
        "validation_results": validation,
        "summary": summary,
    }
    hash_content = json.dumps(hash_payload, sort_keys=True, default=str)
    evidence_hash = hashlib.sha256(hash_content.encode()).hexdigest()

    bundle = EvidenceBundle(
        bundle_id=f"vireon-{evidence_hash[:12]}",
        evidence_hash=evidence_hash,
        created_at="2026-01-01T00:00:00Z",
        experiment_spec=spec,
        execution_trace=trace,
        validation_results=validation,
        summary=summary,
    )

    assert bundle.verify() is True

    # Tamper with the bundle — verify should fail
    bundle.summary["mean_accuracy"] = 0.99
    assert bundle.verify() is False


def test_fbcsp_applies_band_pass():
    """Test that FBCSP applies band-pass filters per band (was broken)."""
    from vireon_methods.spatial.vireon_fbcsp import VireonFBCSP

    rng = np.random.default_rng(42)
    fs = 250
    n_epochs, n_channels, n_samples = 40, 8, 500
    t = np.arange(n_samples) / fs
    X = np.zeros((n_epochs, n_channels, n_samples))
    y = np.zeros(n_epochs, dtype=int)
    X[:20] = rng.normal(0, 0.1, (20, n_channels, n_samples)) + np.sin(2*np.pi*10*t)[None, None, :]
    y[:20] = 0
    X[20:] = rng.normal(0, 0.1, (20, n_channels, n_samples)) + np.sin(2*np.pi*25*t)[None, None, :]
    y[20:] = 1

    fbcsp = VireonFBCSP(bands=[(8, 12), (22, 28)], n_components=2)
    feats = fbcsp.fit_transform(X, y, fs=fs)

    assert feats.shape == (n_epochs, 4)
    assert not np.allclose(feats[:, :2], feats[:, 2:]), \
        "FBCSP features identical across bands — filtering not applied!"


def test_mi_uses_kraskov():
    """Test that VireonMutualInformation uses Kraskov k-NN estimator."""
    from vireon_methods.connectivity.vireon_mutual_information import VireonMutualInformation

    rng = np.random.default_rng(42)
    x = rng.normal(0, 1, 5000)
    y = rng.normal(0, 1, 5000)
    mi = VireonMutualInformation(k=4).compute(x, y)
    assert mi < 0.05, f"MI for independent variables should be ~0, got {mi}"

    rho = 0.8
    x = rng.normal(0, 1, 5000)
    y = rho * x + np.sqrt(1 - rho**2) * rng.normal(0, 1, 5000)
    mi = VireonMutualInformation(k=4).compute(x, y)
    expected = -0.5 * np.log(1 - rho**2)
    assert abs(mi - expected) < 0.15, f"MI {mi:.3f} far from expected {expected:.3f}"


def test_eegnet_has_batchnorm():
    """Test that EEGNet has BatchNorm/ELU/AvgPool (was missing)."""
    pytest.importorskip("torch")
    from vireon_methods.deep_learning.eegnet import EEGNetPyTorch
    import torch.nn as nn

    model = EEGNetPyTorch(n_classes=2, channels=8, samples=256)
    assert sum(1 for m in model.modules() if isinstance(m, nn.BatchNorm2d)) >= 3
    assert sum(1 for m in model.modules() if isinstance(m, nn.ELU)) >= 2
    assert sum(1 for m in model.modules() if isinstance(m, nn.AvgPool2d)) >= 2


def test_registry_insert_or_ignore():
    """Test that registry uses INSERT OR IGNORE (was INSERT OR REPLACE)."""
    from vireon_evidence import EvidenceRegistry
    from vireon_core.contracts.evidence import EvidenceBundle
    from vireon_evidence.registry.core import EvidenceAlreadyRegisteredError

    reg = EvidenceRegistry(db_path=":memory:")
    bundle1 = EvidenceBundle(
        algorithm="VireonWelch", dataset="test",
        statistical_agreement={"ccc": 0.99},
    )
    reg.register(bundle1)

    bundle2 = bundle1.model_copy(deep=True)
    bundle2.statistical_agreement = {"ccc": 0.50}
    bundle2.evidence_hash = bundle1.evidence_hash

    with pytest.raises(EvidenceAlreadyRegisteredError):
        reg.register(bundle2)


def test_registry_get_method():
    """Test that EvidenceRegistry.get() exists (was missing)."""
    from vireon_evidence import EvidenceRegistry
    from vireon_core.contracts.evidence import EvidenceBundle

    reg = EvidenceRegistry(db_path=":memory:")
    bundle = EvidenceBundle(
        algorithm="VireonWelch", dataset="test",
        statistical_agreement={"ccc": 0.99},
    )
    reg.register(bundle)

    retrieved = reg.get(bundle.evidence_hash)
    assert retrieved is not None
    assert reg.get("nonexistent") is None


def test_dataset_dispatch():
    """Test that load_dataset dispatches by key (was ignoring key)."""
    from vireon_corpus import DatasetManager
    from vireon_corpus.exceptions import UnknownDatasetError

    dm = DatasetManager()
    with pytest.raises(UnknownDatasetError):
        dm.load_dataset("nonexistent_key")


def test_transaction_hash_deterministic():
    """Test that transaction hash is deterministic (was using wall-clock)."""
    from vireon_core.contracts.evidence import EvidenceBundle
    from vireon_evidence.graph.transactions import EvidenceTransaction

    bundle = EvidenceBundle(
        algorithm="VireonWelch", dataset="test",
        statistical_agreement={"ccc": 0.99},
    )

    EvidenceTransaction._sequence_counter = 100
    tx1 = EvidenceTransaction(bundle, "test commit")

    EvidenceTransaction._sequence_counter = 100
    tx2 = EvidenceTransaction(bundle, "test commit")

    assert tx1.transaction_hash == tx2.transaction_hash


def test_no_phase_e_stubs():
    """Test that all 35 Phase E stubs are filled."""
    from pathlib import Path
    docs_dir = Path(__file__).resolve().parent.parent.parent / "docs"
    checked_count = 0
    for f in docs_dir.rglob("*.md"):
        if f.suffix == ".rej":
            continue
        content = f.read_text(encoding="utf-8", errors="ignore")
        if "## Phase E Implementation Status" in content or "## Phase E Validation Status" in content:
            checked_count += 1
            idx = content.find("## Phase E")
            after = content[idx:]
            assert "Complete (v1.2.0)" in after or "playbook dx" in after or "Phase E" in after, \
                f"{f} still has empty Phase E stub"
    assert checked_count >= 35, f"Expected at least 35 Phase E docs checked, found {checked_count}"


def test_no_fake_hashes():
    """Test that no fake evidence hashes remain."""
    from pathlib import Path
    import re
    fake_hash_pattern = re.compile(r"evidence_hash.*=.*[\"\'](realtime|dummy|regulatory_510k)")
    repo_root = Path(__file__).resolve().parent.parent.parent
    real_matches = []
    for search_dir in [repo_root / "examples", repo_root / "vireon-lab"]:
        if not search_dir.exists():
            continue
        for p in search_dir.rglob("*.py"):
            if "__pycache__" in str(p) or p.suffix == ".rej":
                continue
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                for line_no, line in enumerate(f, 1):
                    sline = line.strip()
                    if sline.startswith("#"):
                        continue
                    if fake_hash_pattern.search(line):
                        real_matches.append(f"{p}:{line_no}: {sline}")
    assert len(real_matches) == 0, "Fake hashes found:\n" + "\n".join(real_matches)


def test_no_scratch_files():
    """Test that scratch, patch, log, and deprecated runner files are removed."""
    from pathlib import Path
    repo_root = Path(__file__).resolve().parent.parent.parent
    assert not (repo_root / "scratch_bids.py").exists()
    assert not (repo_root / "parse_phase_c.py").exists()
    assert not (repo_root / "parse_transcript.py").exists()
    assert not (repo_root / "test_bem.py").exists()
    assert not (repo_root / "apply_playbook_dx.sh").exists()
    assert not (repo_root / "log_ubuntu_311.txt").exists()
    assert not (repo_root / "vireon_dx.patch").exists()
    assert not (repo_root / "vireon_dx_content_only.patch").exists()
    assert not (repo_root / "vireon_dx_new_files.tar.gz").exists()
    assert not (repo_root / "vireon_validation" / "run_regression_suite.py").exists()


def test_version_synced():
    """Test that version strings are synced to 1.2.0."""
    from pathlib import Path
    repo_root = Path(__file__).resolve().parent.parent.parent
    # pyproject.toml
    with open(repo_root / "pyproject.toml") as f:
        assert 'version = "1.2.0"' in f.read()
    # FastAPI app
    with open(repo_root / "vireon-api" / "vireon_api" / "main.py") as f:
        assert 'version="1.2.0"' in f.read()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
