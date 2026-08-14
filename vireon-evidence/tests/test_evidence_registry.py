from vireon_evidence.registry import EvidenceRegistry
from vireon_core.contracts.evidence import EvidenceBundle


def test_register_and_retrieve(tmp_path):
    db = str(tmp_path / "registry.db")
    reg = EvidenceRegistry(db_path=db)

    bundle = EvidenceBundle(
        evidence_hash="hash1234567890abcdef",
        algorithm="VireonWelch",
        dataset="SyntheticEEG"
    )
    reg.register(bundle)

    retrieved = reg.retrieve("hash1234567890abcdef")
    assert retrieved is not None
    assert retrieved.evidence_hash == "hash1234567890abcdef"
    assert retrieved.algorithm == "VireonWelch"


def test_retrieve_nonexistent(tmp_path):
    db = str(tmp_path / "registry.db")
    reg = EvidenceRegistry(db_path=db)
    assert reg.retrieve("nonexistent") is None


def test_list_bundles_filtering(tmp_path):
    db = str(tmp_path / "registry.db")
    reg = EvidenceRegistry(db_path=db)

    b1 = EvidenceBundle(evidence_hash="h1", algorithm="ICA", dataset="PhysioNet")
    b2 = EvidenceBundle(evidence_hash="h2", algorithm="CSP", dataset="PhysioNet")
    b3 = EvidenceBundle(evidence_hash="h3", algorithm="CSP", dataset="Synthetic")

    reg.register(b1)
    reg.register(b2)
    reg.register(b3)

    assert len(reg.list_bundles()) == 3
    assert len(reg.list_bundles(algorithm="CSP")) == 2
    assert len(reg.list_bundles(dataset="PhysioNet")) == 2
    assert len(reg.list_bundles(algorithm="CSP", dataset="PhysioNet")) == 1


def test_register_rejects_different_content_same_hash(tmp_path):
    """Registering a bundle with an existing hash but different content must raise."""
    import pytest
    from vireon_evidence.exceptions import EvidenceAlreadyRegisteredError
    db = str(tmp_path / "registry.db")
    reg = EvidenceRegistry(db_path=db)

    bundle1 = EvidenceBundle(
        evidence_hash="same_hash_123",
        algorithm="VireonWelch",
        dataset="test",
        statistical_agreement={"ccc": 0.99},
    )
    reg.register(bundle1)

    bundle2 = bundle1.model_copy(deep=True)
    bundle2.statistical_agreement = {"ccc": 0.50}

    with pytest.raises(EvidenceAlreadyRegisteredError):
        reg.register(bundle2)


def test_register_idempotent_for_identical_content(tmp_path):
    """Registering the same bundle twice should be a no-op."""
    db = str(tmp_path / "registry.db")
    reg = EvidenceRegistry(db_path=db)
    bundle = EvidenceBundle(
        evidence_hash="same_hash_456",
        algorithm="VireonWelch",
        dataset="test",
        statistical_agreement={"ccc": 0.99},
    )
    hash1 = reg.register(bundle)
    hash2 = reg.register(bundle)
    assert hash1 == hash2
    assert len(reg.list_bundles()) == 1


def test_update_bundle_creates_new_entry(tmp_path):
    """update_bundle should create a new bundle, not overwrite."""
    db = str(tmp_path / "registry.db")
    reg = EvidenceRegistry(db_path=db)
    bundle1 = EvidenceBundle(
        evidence_hash="orig_hash_789",
        algorithm="VireonWelch",
        dataset="test",
        statistical_agreement={"ccc": 0.99},
    )
    hash1 = reg.register(bundle1)

    bundle2 = bundle1.model_copy(deep=True)
    bundle2.statistical_agreement = {"ccc": 0.95}
    bundle2.supersedes = hash1
    hash2 = reg.update_bundle(bundle2, reason="fixed CCC calculation bug")

    assert hash1 != hash2
    assert reg.retrieve(hash1) is not None
    assert reg.retrieve(hash2) is not None
