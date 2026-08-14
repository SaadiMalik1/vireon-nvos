from vireon_core.contracts.evidence import EvidenceBundle
from vireon_evidence.exporters.report_generator import MultiFormatReportGenerator
from vireon_evidence.graph.core import EvidenceGraph
from vireon_evidence.graph.query import KnowledgeQueryEngine
from vireon_evidence.ontology.nodes import MethodNode, EvidenceBundleNode


def test_multiformat_report_generator():
    bundle = EvidenceBundle(
        evidence_hash="test1234567890abcdef",
        algorithm="CSP",
        dataset="PhysioNet",
        statistical_agreement={"ccc": 0.99, "rmse": 0.001}
    )
    gen = MultiFormatReportGenerator(bundle)
    json_str = gen.generate_json()
    assert "test1234567890abcdef" in json_str

    md_str = gen.generate_markdown()
    assert "# Evidence Bundle:" in md_str
    assert "Bland-Altman" in md_str

    nb = gen.generate_jupyter_notebook()
    assert "cells" in nb


def test_knowledge_query_engine():
    graph = EvidenceGraph()
    m = MethodNode(node_id="test_method", canonical_name="Test Method", version="1.0.0", metadata={"srl": "SRL-3"})
    graph.add_node(m)
    b = EvidenceBundleNode(node_id="b1", rmse=0.01, icc=0.95, status="PASSED", metadata={"method_id": "test_method", "dataset_id": "eeg_domain"})
    graph.add_node(b)
    graph.add_relationship("test_method", "b1", "produced")

    engine = KnowledgeQueryEngine(graph)
    methods = engine.query_methods(min_icc=0.9, dataset_domain="eeg")
    assert len(methods) == 1
    assert methods[0]["method_id"] == "test_method"

    workflows = engine.query_workflows()
    assert isinstance(workflows, list)
