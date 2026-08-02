import pytest
from vireon_core.contracts.evidence import EvidenceBundle, DatasetProvenance
from vireon_evidence.ontology.nodes import EvidenceBundleNode

def test_evidence_bundle_to_node_and_back():
    bundle = EvidenceBundle(
        bundle_id="b-12345",
        algorithm="CSP",
        dataset="CHB-MIT",
        pass_fail="PASS",
        metrics={"rmse": 1e-5, "icc": 0.995, "ccc": 0.994},
        srl_recommendation="SRL-4"
    )
    
    node = EvidenceBundleNode.from_evidence_bundle(bundle)
    assert node.node_id == "b-12345"
    assert node.node_type == "EvidenceBundle"
    assert node.rmse == 1e-5
    assert node.icc == 0.995
    assert node.status == "PASS"
    assert node.metadata.get("algorithm") == "CSP"
    assert node.metadata.get("dataset") == "CHB-MIT"
    assert node.metadata.get("srl_recommendation") == "SRL-4"
    
    round_trip_bundle = node.to_evidence_bundle()
    assert round_trip_bundle.bundle_id == bundle.bundle_id
    assert round_trip_bundle.algorithm == bundle.algorithm
    assert round_trip_bundle.dataset == bundle.dataset
    assert round_trip_bundle.pass_fail == bundle.pass_fail
    assert round_trip_bundle.metrics.get("rmse") == 1e-5
    assert round_trip_bundle.srl_recommendation == "SRL-4"

def test_evidence_bundle_node_to_bundle_defaults():
    node = EvidenceBundleNode(
        node_id="b-999",
        rmse=0.001,
        icc=0.98,
        status="PASSED",
        metadata={"algorithm": "Welch", "dataset": "EEGBCI"}
    )
    
    bundle = node.to_evidence_bundle()
    assert bundle.bundle_id == "b-999"
    assert bundle.algorithm == "Welch"
    assert bundle.dataset == "EEGBCI"
    assert bundle.pass_fail == "PASSED"
    assert bundle.metrics["rmse"] == 0.001
    assert bundle.metrics["icc"] == 0.98
