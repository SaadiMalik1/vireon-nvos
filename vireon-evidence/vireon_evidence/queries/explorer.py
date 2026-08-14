import re
from typing import List, Dict, Any
from vireon_evidence.graph.core import EvidenceGraph

class EvidenceExplorer:
    """
    Implements a graph query language engine.
    e.g. MATCH Method WHERE supports CHB-MIT AND CCC > 0.99
    """
    def __init__(self, graph: EvidenceGraph):
        self.graph = graph
        
    def execute_query(self, query_string: str) -> List[Dict[str, Any]]:
        """
        Parses and executes a declarative graph query string.
        """
        results = []
        # Pattern 1: MATCH Method WHERE supports <dataset> AND CCC > <val>
        match_pattern = re.search(r"MATCH\s+(\w+)\s+WHERE\s+(.*)", query_string, re.IGNORECASE)
        if match_pattern:
            target_entity = match_pattern.group(1).lower()
            conditions_str = match_pattern.group(2)
            
            # Parse conditions
            dataset_match = re.search(r"supports\s+([\w\-]+)", conditions_str, re.IGNORECASE)
            ccc_match = re.search(r"CCC\s*([><=]+)\s*([0-9\.]+)", conditions_str, re.IGNORECASE)
            
            target_dataset = dataset_match.group(1) if dataset_match else None
            ccc_op = ccc_match.group(1) if ccc_match else None
            ccc_thresh = float(ccc_match.group(2)) if ccc_match else None
            
            if target_entity == "method":
                methods = self.graph.get_methods()
                for m in methods:
                    m_id = m["node_id"]
                    m_name = m.get("canonical_name", m_id)
                    bundles = self.graph.get_evidence_for_method(m_id)
                    for b in bundles:
                        meta = b.get("metadata", {})
                        d_id = meta.get("dataset_id", "")
                        b_ccc = meta.get("ccc") or b.get("icc") or 0.0
                        
                        match_ds = (target_dataset is None or 
                                    target_dataset.lower() in d_id.lower() or 
                                    target_dataset.lower() in str(self.graph._graph.nodes.get(d_id, {})).lower() or
                                    self.graph._graph.has_edge(b.get("node_id", ""), target_dataset))
                        
                        match_metric = True
                        if ccc_op == ">" and b_ccc <= ccc_thresh:
                            match_metric = False
                        elif ccc_op == ">=" and b_ccc < ccc_thresh:
                            match_metric = False
                        elif ccc_op == "<" and b_ccc >= ccc_thresh:
                            match_metric = False
                            
                        if match_ds and match_metric:
                            results.append({
                                "node": m_name,
                                "method_id": m_id,
                                "ccc": b_ccc,
                                "dataset": d_id or target_dataset
                            })
        return results
