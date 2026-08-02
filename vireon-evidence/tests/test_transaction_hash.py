import pytest
from vireon_core.contracts.evidence import EvidenceBundle, DatasetProvenance
from vireon_evidence.graph.transactions import EvidenceTransaction
from pydantic import BaseModel

def create_bundle(verdict="PASS"):
    return EvidenceBundle(
        bundle_id="x",
        timestamp="2023-01-01T00:00:00",
        dataset="test_dataset",
        campaign_class="test_campaign",
        method_provenance=[],
        dataset_provenance=DatasetProvenance(dataset_id="x", version="1", checksum="abc", acquisition_date="2023", modalities=[], sampling_rate=1.0, doi="x", bids_version="x", download_url="x", hash_checksum="x"),
        assumptions=[],
        perturbation="none",
        clinical_domains_supported=[],
        known_limitations=[],
        statistical_agreement={"rmse": 0.0},
        conclusion_verdict=verdict,
        srl_recommendation="SRL_2",
        author="test_author"
    )

def test_different_bundles_different_hashes():
    b1 = create_bundle(verdict="PASS")
    b2 = create_bundle(verdict="FAIL")
    t1 = EvidenceTransaction(bundle=b1, message="m")
    t2 = EvidenceTransaction(bundle=b2, message="m")
    assert t1.transaction_hash != t2.transaction_hash

def test_same_bundle_same_hash():
    b = create_bundle()
    t1 = EvidenceTransaction(bundle=b, message="m")
    t2 = EvidenceTransaction(bundle=b, message="m")
    assert t1.transaction_hash == t2.transaction_hash

def test_tampered_bundle_fails_verification():
    b = create_bundle()
    t = EvidenceTransaction(bundle=b, message="m")
    b.conclusion_verdict = "TAMPERED"  # mutate
    assert t.verify_integrity(b) is False
