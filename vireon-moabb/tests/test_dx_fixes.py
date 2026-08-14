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
    import subprocess
    result = subprocess.run(
        ["grep", "-rl", "## Phase E Implementation Status", "docs/"],
        capture_output=True, text=True
    )
    # Should still have the header, but now with content
    # Check that none are empty stubs (just the header + empty NOTE)
    for f in result.stdout.strip().split("\n"):
        if not f:
            continue
        content = open(f).read()
        # Should have substantive content after the header
        idx = content.find("## Phase E Implementation Status")
        after = content[idx:]
        # Should be more than just the header + "> [!NOTE]"
        assert "Complete (v1.2.0)" in after or "playbook dx" in after, \
            f"{f} still has empty Phase E stub"


def test_no_fake_hashes():
    """Test that no fake evidence hashes remain."""
    import subprocess
    result = subprocess.run(
        ["grep", "-rn", "-E",
         'evidence_hash.*=.*"realtime|evidence_hash.*=.*"dummy|evidence_hash.*=.*"regulatory_510k',
         "examples/", "vireon-lab/"],
        capture_output=True, text=True
    )
    # Should be empty (or only comments)
    real_matches = [l for l in result.stdout.split("\n") if l and not l.strip().startswith("#")]
    assert len(real_matches) == 0, f"Fake hashes found:\n{result.stdout}"


def test_no_scratch_files():
    """Test that scratch files with /home/ronin paths are removed."""
    assert not os.path.exists("scratch_bids.py")
    assert not os.path.exists("parse_phase_c.py")
    assert not os.path.exists("parse_transcript.py")
    assert not os.path.exists("test_bem.py")


def test_version_synced():
    """Test that version strings are synced to 1.2.0."""
    import subprocess
    # pyproject.toml
    with open("pyproject.toml") as f:
        assert 'version = "1.2.0"' in f.read()
    # FastAPI app
    with open("vireon-api/vireon_api/main.py") as f:
        assert 'version="1.2.0"' in f.read()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
