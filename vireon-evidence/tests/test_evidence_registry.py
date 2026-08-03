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
