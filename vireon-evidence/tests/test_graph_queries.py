import pytest
import numpy as np
from vireon_evidence.graph.core import EvidenceGraph
from vireon_evidence.ontology.nodes import MethodNode, DatasetNode, EvidenceBundleNode, ScientificClaimNode, PublicationNode
from vireon_evidence.queries.leaderboard import ScientificLeaderboard, LeaderboardCategory
from vireon_evidence.queries.query_engine import ScientificQueryEngine
from vireon_evidence.queries.explorer import EvidenceExplorer
from vireon_evidence.queries.timeline import ScientificTimeline
from vireon_evidence.queries.meta_analysis import ContinuousMetaAnalysis
from vireon_evidence.services.evidence_service import EvidenceService

@pytest.fixture
def populated_graph():
    graph = EvidenceGraph()
    
    # Add methods
    m1 = MethodNode(node_id="mne_csp", canonical_name="MNE CSP", version="1.4", metadata={"srl": "SRL-4", "type": "CSP"})
    m2 = MethodNode(node_id="vireon_csp", canonical_name="VIREON CSP", version="0.1", metadata={"srl": "SRL-3", "type": "CSP"})
    m3 = MethodNode(node_id="scipy_welch", canonical_name="SciPy Welch", version="1.11", metadata={"srl": "SRL-5", "type": "PSD"})
    graph.add_node(m1)
    graph.add_node(m2)
    graph.add_node(m3)
    
    # Add datasets
    d1 = DatasetNode(node_id="chb_mit", bids_version="1.0", doi="10.1016/chbmit", metadata={"name": "CHB-MIT"})
    d2 = DatasetNode(node_id="eegbci", bids_version="1.0", doi="10.1016/eegbci", metadata={"name": "EEGBCI"})
    graph.add_node(d1)
    graph.add_node(d2)
    
    # Add bundles
    b1 = EvidenceBundleNode(
        node_id="b1",
        rmse=1e-6,
        icc=0.998,
        status="PASSED",
        metadata={"method_id": "mne_csp", "dataset_id": "chb_mit", "ccc": 0.998, "execution_time_ms": 12.0, "timestamp": "2026-02-01"}
    )
    b2 = EvidenceBundleNode(
        node_id="b2",
        rmse=1.2e-6,
        icc=0.995,
        status="PASSED",
        metadata={"method_id": "mne_csp", "dataset_id": "eegbci", "ccc": 0.995, "execution_time_ms": 14.0, "timestamp": "2026-03-01"}
    )
    b3 = EvidenceBundleNode(
        node_id="b3",
        rmse=2.5e-6,
        icc=0.980,
        status="PASSED",
        metadata={"method_id": "vireon_csp", "dataset_id": "chb_mit", "ccc": 0.980, "execution_time_ms": 8.0, "timestamp": "2026-01-15"}
    )
    b4 = EvidenceBundleNode(
        node_id="b4",
        rmse=5.0e-5,
        icc=0.850,
        status="FAILED",
        metadata={"method_id": "vireon_csp", "dataset_id": "eegbci", "ccc": 0.850, "execution_time_ms": 9.0, "timestamp": "2026-04-01"}
    )
    graph.add_node(b1)
    graph.add_node(b2)
    graph.add_node(b3)
    graph.add_node(b4)
    
    # Add relationships
    graph.add_relationship("mne_csp", "b1", "produced")
    graph.add_relationship("b1", "chb_mit", "evaluated_on")
    
    graph.add_relationship("mne_csp", "b2", "produced")
    graph.add_relationship("b2", "eegbci", "evaluated_on")
    
    graph.add_relationship("vireon_csp", "b3", "produced")
    graph.add_relationship("b3", "chb_mit", "evaluated_on")
    
    graph.add_relationship("vireon_csp", "b4", "produced")
    graph.add_relationship("b4", "eegbci", "evaluated_on")
    
    # Add publication & claim
    p1 = PublicationNode(node_id="pub1", doi="10.1016/j.clinph.2018.04.015", title="Canonical CSP Benchmark")
    graph.add_node(p1)
    graph.add_relationship("mne_csp", "pub1", "references")
    
    return graph

def test_leaderboard(populated_graph):
    lb = ScientificLeaderboard(populated_graph)
    results = lb.generate(category=LeaderboardCategory.HIGHEST_CONFIDENCE, method_type="CSP")
    assert len(results) >= 2
    # MNE CSP should be ranked #1 because its average ccc is (0.998+0.995)/2 = 0.9965 vs vireon_csp (0.980+0.850)/2 = 0.915
    assert results[0]["method"] == "MNE CSP"
    assert results[0]["rank"] == 1
    assert results[0]["ccc"] > results[1]["ccc"]

def test_query_engine(populated_graph):
    qe = ScientificQueryEngine(populated_graph)
    # Query methods on chb_mit with ccc >= 0.99
    res = qe.query_methods_by_dataset_and_metric("chb_mit", {"ccc": 0.99})
    assert "mne_csp" in res
    assert "vireon_csp" not in res # ccc is 0.980

    # Query reproduction failures
    failures = qe.query_reproduction_failures()
    assert len(failures) >= 1

def test_explorer_declarative_query(populated_graph):
    exp = EvidenceExplorer(populated_graph)
    results = exp.execute_query("MATCH Method WHERE supports chb_mit AND CCC > 0.99")
    assert len(results) == 1
    assert results[0]["node"] == "MNE CSP"

def test_timeline(populated_graph):
    tl = ScientificTimeline(populated_graph)
    events = tl.generate_timeline("mne_csp")
    assert len(events) >= 2
    # Check that events are ordered by date
    assert events[0]["date"] <= events[1]["date"]

def test_meta_analysis_recompute(populated_graph):
    ma = ContinuousMetaAnalysis(populated_graph)
    meta = ma.recompute("mne_csp")
    assert meta["method_id"] == "mne_csp"
    assert meta["n_studies"] == 2
    assert 0.99 <= meta["overall_confidence"] <= 1.0
    assert "confidence_interval" in meta
    assert len(meta["confidence_interval"]) == 2
    assert meta["heterogeneity_i2"] >= 0.0

def test_evidence_service(populated_graph):
    svc = EvidenceService(populated_graph)
    profile = svc.get_method_profile("mne_csp")
    assert profile["method"] == "mne_csp"
    assert profile["total_benchmarks"] == 2
    assert "chb_mit" in profile["datasets"] or "CHB-MIT" in profile["datasets"] or "chb_mit" in profile["datasets"]
    assert profile["metrics"]["ccc"] > 0.99
