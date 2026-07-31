from vireon_core.contracts.evidence import EvidenceBundle
from vireon_evidence.graph.core import EvidenceGraph
import datetime

class EvidenceTransaction:
    """
    Immutable transaction for appending to the Evidence Graph.
    Operates like a Git commit.
    """
    def __init__(self, bundle: EvidenceBundle, message: str = ""):
        self.bundle = bundle
        self.message = message
        self.timestamp = datetime.datetime.utcnow().isoformat()
        self.transaction_hash = self._compute_hash()
        
    def _compute_hash(self) -> str:
        # Stubbed cryptographic hash of the transaction
        import hashlib
        payload = f"{self.bundle.bundle_id}:{self.timestamp}:{self.message}"
        return hashlib.sha256(payload.encode()).hexdigest()

class GraphCommitter:
    def __init__(self, graph: EvidenceGraph):
        self.graph = graph
        
    def commit(self, transaction: EvidenceTransaction):
        """
        Appends the Evidence Bundle as a node and links it immutably.
        """
        # Node generation stub
        from vireon_evidence.ontology.nodes import EvidenceBundleNode
        
        node = EvidenceBundleNode(
            node_id=transaction.bundle.bundle_id,
            rmse=transaction.bundle.statistical_agreement.get("rmse"),
            icc=transaction.bundle.statistical_agreement.get("ccc"),
            status=transaction.bundle.conclusion_verdict,
            metadata={"transaction_hash": transaction.transaction_hash, "timestamp": transaction.timestamp}
        )
        
        self.graph.add_node(node)
        # Link to method
        for m in transaction.bundle.method_provenance:
            self.graph.add_relationship(m.plugin_id, node.node_id, "generated")
            
        # Link to dataset
        self.graph.add_relationship(node.node_id, transaction.bundle.dataset_provenance.dataset_id, "validated_on")
