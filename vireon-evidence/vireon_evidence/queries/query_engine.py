import networkx as nx
from typing import List, Dict, Any, Optional, Union
from vireon_evidence.graph.core import EvidenceGraph


class ScientificQueryEngine:
    """
    Searchable scientific knowledge system over the Evidence Graph.
    """
    def __init__(self, graph: EvidenceGraph):
        self.graph = graph

    def query_methods_by_dataset_and_metric(
        self,
        dataset_id: str,
        metric_conditions: Optional[Union[Dict[str, Any], float]] = None,
        min_ccc: Optional[float] = None
    ) -> List[Any]:
        """
        Query methods executed on dataset_id matching metric conditions.
        Supports:
        - min_ccc keyword argument (or float metric_conditions) -> List[Dict] with {"method", "ccc", "hash"} sorted descending by CCC
        - dict metric_conditions: {"ccc": 0.99, "rmse": 1e-5} -> List[str] of method IDs
        """
        if min_ccc is not None or isinstance(metric_conditions, (int, float)):
            threshold = float(min_ccc if min_ccc is not None else metric_conditions)
            results = []
            for node_id, data in self.graph._graph.nodes(data=True):
                node_data = data.get("data", data)
                if node_data.get("node_type") == "EvidenceBundle" or data.get("node_type") == "EvidenceBundle":
                    meta = node_data.get("metadata", {})
                    d_id = node_data.get("dataset") or meta.get("dataset_id")
                    if d_id == dataset_id:
                        stat_aggr = node_data.get("statistical_agreement", {})
                        ccc = stat_aggr.get("ccc") if isinstance(stat_aggr, dict) else None
                        if ccc is None:
                            ccc = meta.get("ccc") or node_data.get("icc")
                        if ccc is not None and ccc >= threshold:
                            method = node_data.get("algorithm") or meta.get("method_id")
                            h = node_data.get("evidence_hash") or node_data.get("node_id")
                            results.append({"method": method, "ccc": float(ccc), "hash": h})
            return sorted(results, key=lambda x: -x["ccc"])

        if metric_conditions is None:
            metric_conditions = {}

        matched_methods = []
        methods = self.graph.get_methods()
        for m in methods:
            m_id = m["node_id"]
            bundles = self.graph.get_evidence_for_method(m_id)
            for b in bundles:
                b_id = b["node_id"]
                meta = b.get("metadata", {})
                is_connected = False
                if meta.get("dataset_id") == dataset_id or b.get("dataset") == dataset_id:
                    is_connected = True
                elif self.graph._graph.has_edge(b_id, dataset_id) or self.graph._graph.has_edge(dataset_id, b_id):
                    is_connected = True
                elif nx.has_path(self.graph._graph, m_id, dataset_id):
                    is_connected = True

                if is_connected:
                    passes = True
                    if "ccc" in metric_conditions:
                        ccc = meta.get("ccc") or b.get("icc")
                        if ccc is None or ccc < metric_conditions["ccc"]:
                            passes = False
                    if "rmse" in metric_conditions:
                        rmse = b.get("rmse")
                        if rmse is None or rmse > metric_conditions["rmse"]:
                            passes = False
                    if "icc" in metric_conditions:
                        icc = b.get("icc")
                        if icc is None or icc < metric_conditions["icc"]:
                            passes = False
                    if passes:
                        if m_id not in matched_methods:
                            matched_methods.append(m_id)
        return matched_methods

    def query_srl_readiness(self, target_srl: str, domain: Optional[str] = None) -> List[str]:
        """Find methods qualifying for target_srl."""
        methods = self.graph.get_methods()
        matched = []
        for m in methods:
            m_id = m["node_id"]
            meta = m.get("metadata", {})
            srl = meta.get("srl", "SRL-0")
            if srl >= target_srl:
                matched.append(m_id)
        return matched

    def query_reproduction_failures(self, reference_software_version: Optional[str] = None) -> List[str]:
        """Find failed reproduction bundles or claims."""
        failures = []
        for node_id, data in self.graph._graph.nodes(data=True):
            if data.get("node_type") == "EvidenceBundle" and data.get("status") == "FAILED":
                failures.append(node_id)
            elif data.get("node_type") == "ScientificClaim" and data.get("verdict") == "FAILED":
                failures.append(node_id)
        return failures
