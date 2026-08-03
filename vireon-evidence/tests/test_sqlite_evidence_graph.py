from vireon_evidence.graph.core import EvidenceGraph
from vireon_evidence.ontology.nodes import MethodNode, DatasetNode


def test_graph_persists_to_sqlite(tmp_path):
    db = str(tmp_path / "test.db")
    g1 = EvidenceGraph(db_path=db)
    g1.add_node(MethodNode(node_id="test", canonical_name="Test", version="1.0"))
    g1.persist()

    # New instance loads from DB
    g2 = EvidenceGraph(db_path=db)
    assert "test" in g2.list_nodes()


def test_graph_edges_persist(tmp_path):
    db = str(tmp_path / "test.db")
    g1 = EvidenceGraph(db_path=db)
    g1.add_node(MethodNode(node_id="m1", canonical_name="M", version="1.0"))
    g1.add_node(DatasetNode(node_id="d1", bids_version="1.0", doi=None))
    g1.add_relationship("m1", "d1", "validated_on")
    g1.persist()

    g2 = EvidenceGraph(db_path=db)
    assert g2._graph.has_edge("m1", "d1")
