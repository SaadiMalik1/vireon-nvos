from vireon_core.contracts.evidence import EvidenceBundle, DatasetProvenance, MethodProvenance
from vireon_evidence.graph.core import EvidenceGraph
from vireon_evidence.graph.transactions import EvidenceTransaction, GraphCommitter

def test_graph_committer_handles_perturbation():
    bundle = EvidenceBundle(
        bundle_id="b_test_001",
        algorithm="CSP_LDA",
        dataset="PhysioNet",
        campaign_class="Robustness",
        perturbation="white_noise_0.5",
        method_provenance=[
            MethodProvenance(plugin_id="csp_lda", version="1.0", srl="SRL_3", scientific_contract_hash="hash")
        ],
        dataset_provenance=DatasetProvenance(
            dataset_id="ds_physionet",
            bids_version="1.0",
            hash_checksum="abc",
            doi="10.1234/test",
            download_url="https://example.com"
        ),
        conclusion_verdict="PASS",
        srl_recommendation="SRL_3"
    )
    
    graph = EvidenceGraph()
    committer = GraphCommitter(graph)
    tx = EvidenceTransaction(bundle=bundle, message="Commit test bundle")
    
    # Must not fail with AttributeError: 'EvidenceBundle' object has no attribute 'perturbations'
    committer.commit(tx)
    
    # Check that perturbation node and relationship exist
    edges = [(u, v, data.get("type")) for u, v, data in graph._graph.edges(data=True)]
    assert any(rel == "subject_to" for _, _, rel in edges)
    assert any("white_noise" in target for _, target, rel in edges if rel == "subject_to")
