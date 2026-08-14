from vireon_evidence.doi import EvidenceIdentifier
from vireon_core.contracts.evidence import EvidenceBundle


def test_mint_doi():
    minter = EvidenceIdentifier(prefix="10.5072/vireon")
    bundle = EvidenceBundle(
        evidence_hash="abcdef1234567890extrahash",
        algorithm="VireonICA",
        dataset="PhysioNet"
    )
    doi = minter.mint(bundle)
    assert doi == "10.5072/vireon/abcdef1234567890"


def test_mint_with_metadata():
    minter = EvidenceIdentifier(prefix="10.5072/vireon")
    bundle = EvidenceBundle(
        evidence_hash="abcdef1234567890extrahash",
        algorithm="VireonICA",
        dataset="PhysioNet"
    )
    meta = minter.mint_with_metadata(bundle)
    assert meta["doi"] == "10.5072/vireon/abcdef1234567890"
    assert "VireonICA" in meta["title"]
    assert "PhysioNet" in meta["title"]
    assert meta["publisher"] == "VIREON"
