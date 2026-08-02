from typing import List, Dict, Any, Optional

class KnowledgeQueryEngine:
    """
    Transforms the EvidenceGraph into a reusable, queryable scientific database.
    """
    def __init__(self, graph_db):
        self.graph = graph_db
        
    def query_methods(self, dataset_domain: Optional[str] = None, min_icc: Optional[float] = None, 
                      clinical_use: Optional[str] = None, max_complexity: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Executes semantic queries across the knowledge graph.
        """
        results = []
        if hasattr(self.graph, "get_methods"):
            methods = self.graph.get_methods()
        elif hasattr(self.graph, "_graph"):
            methods = [{"node_id": n, **d} for n, d in self.graph._graph.nodes(data=True) if d.get("node_type") == "Method"]
        else:
            methods = []
            
        for m in methods:
            m_id = m.get("node_id", "")
            meta = m.get("metadata", {})
            bundles = self.graph.get_evidence_for_method(m_id) if hasattr(self.graph, "get_evidence_for_method") else []
            
            iccs = [b.get("icc") or b.get("metadata", {}).get("ccc") for b in bundles if (b.get("icc") is not None or b.get("metadata", {}).get("ccc") is not None)]
            avg_icc = float(sum(iccs) / len(iccs)) if iccs else 0.0
            
            datasets = [b.get("metadata", {}).get("dataset_id") for b in bundles if b.get("metadata", {}).get("dataset_id")]
            
            if min_icc is not None and avg_icc < min_icc:
                continue
            if dataset_domain is not None and not any(dataset_domain.lower() in d.lower() for d in datasets):
                continue
                
            results.append({
                "method": m.get("canonical_name", m_id),
                "method_id": m_id,
                "version": m.get("version", "1.0.0"),
                "validated_datasets": datasets,
                "icc_score": avg_icc,
                "srl": meta.get("srl", "SRL-0"),
            })
            
        return results
        
    def query_workflows(self, includes_method: Optional[str] = None, validated_on: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Finds workflows matching criteria.
        """
        workflows = []
        if hasattr(self.graph, "_graph"):
            for node_id, data in self.graph._graph.nodes(data=True):
                if data.get("node_type") == "Workflow":
                    workflows.append({"workflow_id": node_id, **data})
        return workflows
