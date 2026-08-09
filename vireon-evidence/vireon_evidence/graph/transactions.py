from typing import Optional
from vireon_core.contracts.evidence import EvidenceBundle
from vireon_evidence.graph.core import EvidenceGraph
import datetime

class EvidenceTransaction:
    """Immutable transaction for appending to the Evidence Graph.
    Operates like a Git commit.

    The transaction_hash is computed from bundle_id, message, bundle_json,
    and parent_hash (if set) — NOT wall-clock time. This ensures that committing
    the same bundle twice produces identical transaction hashes.
    """

    _sequence_counter = 0

    def __init__(
        self,
        bundle: EvidenceBundle,
        message: str = "",
        parent_hash: Optional[str] = None,
        sequence_number: Optional[int] = None,
    ):
        self.bundle = bundle
        self.message = message
        self.parent_hash = parent_hash
        if sequence_number is not None:
            self.sequence_number = sequence_number
        else:
            EvidenceTransaction._sequence_counter += 1
            self.sequence_number = EvidenceTransaction._sequence_counter
        self.wall_clock = datetime.datetime.utcnow().isoformat()
        self.timestamp = self.wall_clock
        self.transaction_hash = self._compute_hash()

    def _compute_hash(self) -> str:
        import hashlib
        bundle_json = self.bundle.model_dump_json(
            exclude_none=True,
            serialize_as_any=True,
        )
        payload = f"{self.bundle.bundle_id}:{self.message}:{bundle_json}"
        if self.parent_hash:
            payload += f":{self.parent_hash}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def verify_integrity(self, bundle: EvidenceBundle) -> bool:
        import hashlib
        bundle_json = bundle.model_dump_json(
            exclude_none=True,
            serialize_as_any=True,
        )
        payload = f"{bundle.bundle_id}:{self.message}:{bundle_json}"
        if self.parent_hash:
            payload += f":{self.parent_hash}"
        computed_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        return self.transaction_hash == computed_hash

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
            
        # Expanded Hierarchical Flow
        # Method -> Campaign -> Perturbation Sweep -> Dataset -> Evidence -> Scientific Claim -> Consensus
        
        # Method -> Campaign
        campaign_node_id = f"campaign_{transaction.bundle.bundle_id}"
        for m in transaction.bundle.method_provenance:
            self.graph.add_relationship(m.plugin_id, campaign_node_id, "executed_in")
            
        # Campaign -> Perturbation
        perturbation_node_id = f"perturbation_{transaction.bundle.perturbation}"
        self.graph.add_relationship(campaign_node_id, perturbation_node_id, "under_condition")
        
        # Method -> Mathematical Assumptions
        for assumption in transaction.bundle.assumptions:
            assumption_node_id = f"assumption_{assumption}"
            for m in transaction.bundle.method_provenance:
                self.graph.add_relationship(m.plugin_id, assumption_node_id, "assumes")
                
        # Method -> Known Limitations
        for limitation in transaction.bundle.known_limitations:
            limit_node_id = f"limitation_{limitation}"
            for m in transaction.bundle.method_provenance:
                self.graph.add_relationship(m.plugin_id, limit_node_id, "limited_by")
                
        # Method -> Clinical Domains
        for domain in transaction.bundle.clinical_domains_supported:
            domain_node_id = f"clinical_domain_{domain}"
            for m in transaction.bundle.method_provenance:
                self.graph.add_relationship(m.plugin_id, domain_node_id, "validated_for")
                
        # Perturbation -> Dataset
        self.graph.add_relationship(perturbation_node_id, transaction.bundle.dataset_provenance.dataset_id, "applied_to")
        
        # Dataset -> Evidence
        self.graph.add_relationship(transaction.bundle.dataset_provenance.dataset_id, node.node_id, "produced")
        
        # Evidence -> Scientific Claim
        claim_node_id = f"claim_{transaction.bundle.srl_recommendation}"
        self.graph.add_relationship(node.node_id, claim_node_id, "supports")
        
        # Domain Extensions
        if transaction.bundle.connectivity_metric:
            network_node = f"network_{transaction.bundle.connectivity_metric}"
            self.graph.add_relationship(node.node_id, network_node, "quantifies_network")
            
        if transaction.bundle.head_model:
            head_model_node = f"headmodel_{transaction.bundle.head_model}"
            self.graph.add_relationship(node.node_id, head_model_node, "localized_via")
            
        # Global Campaign Entities
        dataset_node_id = f"dataset_{transaction.bundle.dataset}"
        protocol_node_id = f"protocol_{transaction.bundle.campaign_class}"
        self.graph.add_relationship(node.node_id, dataset_node_id, "evaluated_on")
        self.graph.add_relationship(node.node_id, protocol_node_id, "executed_via")
        
        # Workflow Architecture Additions
        if hasattr(transaction.bundle, 'workflow_id') and transaction.bundle.workflow_id:
            workflow_node_id = f"workflow_{transaction.bundle.workflow_id}"
            self.graph.add_relationship(workflow_node_id, node.node_id, "comprises_algorithm")
            self.graph.add_relationship(workflow_node_id, dataset_node_id, "validated_on_dataset")
            
        if transaction.bundle.perturbation:
            perturb_node_id = f"perturbation_{transaction.bundle.perturbation}"
            self.graph.add_relationship(node.node_id, perturb_node_id, "subject_to")
            
        if transaction.bundle.pass_fail == "FAIL":
            failure_node_id = f"failure_mode_{transaction.bundle.srl_recommendation}"
            self.graph.add_relationship(node.node_id, failure_node_id, "exhibits_failure")
            
        # Scientific Claim -> Consensus
        consensus_node_id = "consensus_srl"
        self.graph.add_relationship(claim_node_id, consensus_node_id, "contributes_to")
