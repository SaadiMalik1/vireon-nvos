from vireon_core.contracts.evidence import EvidenceBundle
from vireon_evidence.exporters.format_exporters import (
    export_to_jsonld,
    export_to_bibtex,
    export_to_turtle,
)


def test_export_to_jsonld():
    bundle = EvidenceBundle(
        evidence_hash="abcdef1234567890abcdef1234567890",
        algorithm="VireonWelch",
        dataset="SyntheticEEG"
    )
    jsonld = export_to_jsonld(bundle)
    assert jsonld["@context"] == "https://schema.org"
    assert jsonld["@type"] == "Dataset"
    assert jsonld["name"] == "VIREON Evidence: VireonWelch"
    assert "https://saadimalik1.github.io/vireon-nvos/evidence/abcdef1234567890abcdef1234567890" in jsonld["@id"]


def test_export_to_bibtex():
    bundle = EvidenceBundle(
        evidence_hash="abcdef1234567890abcdef1234567890",
        algorithm="VireonWelch",
        dataset="SyntheticEEG"
    )
    bib = export_to_bibtex(bundle)
    assert "@dataset{abcdef1234567890," in bib
    assert "title = {VIREON Evidence: VireonWelch}" in bib
    assert "doi = {10.5072/vireon/abcdef1234567890}" in bib


def test_export_to_turtle():
    bundle = EvidenceBundle(
        evidence_hash="abcdef1234567890abcdef1234567890",
        algorithm="VireonWelch",
        dataset="SyntheticEEG"
    )
    ttl = export_to_turtle(bundle)
    assert "schema:Dataset" in ttl
    assert 'schema:name "VIREON Evidence: VireonWelch"' in ttl
