import sqlite3
import json
from typing import List, Dict, Any, Optional
import networkx as nx
from vireon_evidence.ontology.nodes import EvidenceNode, DatasetNode, MethodNode, EvidenceBundleNode, ScientificClaimNode


class EvidenceGraph:
    """
    The Scientific Evidence Graph with optional SQLite persistence.
    Uses networkx to store nodes (datasets, methods, evidence bundles, claims) and directed edges (relationships).
    """
    def __init__(self, db_path: Optional[str] = None):
        self._graph = nx.DiGraph()
        self.db_path = db_path
        self.conn = None
        if db_path:
            self._init_db()
            self._load_from_db()

    def _init_db(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS nodes (
                node_id TEXT PRIMARY KEY,
                node_type TEXT,
                data JSON
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS edges (
                source TEXT,
                target TEXT,
                relation TEXT,
                PRIMARY KEY (source, target, relation)
            )
        """)
        self.conn.commit()

    def _load_from_db(self):
        if not self.conn:
            return
        cur = self.conn.execute("SELECT node_id, data FROM nodes")
        for node_id, data_json in cur:
            data = json.loads(data_json)
            self._graph.add_node(node_id, **data)
        cur = self.conn.execute("SELECT source, target, relation FROM edges")
        for source, target, relation in cur:
            self._graph.add_edge(source, target, relation=relation, type=relation)

    def add_node(self, node: Any):
        if hasattr(node, "model_dump"):
            data = node.model_dump()
            node_id = getattr(node, "node_id", str(node))
            node_type = getattr(node, "node_type", "Unknown")
        elif isinstance(node, dict):
            data = node
            node_id = node.get("node_id", str(node))
            node_type = node.get("node_type", "Unknown")
        else:
            data = {"node_id": str(node)}
            node_id = str(node)
            node_type = "Unknown"

        self._graph.add_node(node_id, **data)
        if self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO nodes VALUES (?, ?, ?)",
                (node_id, str(node_type), json.dumps(data, default=str))
            )
            self.conn.commit()

    def add_relationship(self, source_id: str, target_id: str, relationship_type: str):
        self._graph.add_edge(source_id, target_id, relation=relationship_type, type=relationship_type)
        if self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO edges VALUES (?, ?, ?)",
                (str(source_id), str(target_id), str(relationship_type))
            )
            self.conn.commit()

    def persist(self):
        """Flush in-memory graph to SQLite."""
        if self.conn:
            self.conn.commit()

    def list_nodes(self) -> List[str]:
        return list(self._graph.nodes)

    def query_methods_by_dataset(self, dataset_id: str) -> List[Dict[str, Any]]:
        """
        Query example: which methods have been executed on this dataset?
        """
        results = []
        if not self._graph.has_node(dataset_id):
            return results

        for node, data in self._graph.nodes(data=True):
            if data.get("type") == "method" or data.get("node_type") == "Method":
                if nx.has_path(self._graph, node, dataset_id):
                    paths = list(nx.all_simple_paths(self._graph, node, dataset_id))
                    if paths:
                        results.append({
                            "method_id": node,
                            "method_name": data.get("name", node),
                            "paths": paths
                        })
        return results

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        if self._graph.has_node(node_id):
            return self._graph.nodes[node_id]
        return None

    def get_methods(self, method_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all method nodes, optionally filtered by method_type."""
        methods = []
        for node_id, data in self._graph.nodes(data=True):
            if data.get("node_type") == "Method":
                m_type = data.get("metadata", {}).get("type") or data.get("type")
                if method_type is None or m_type == method_type:
                    methods.append({"node_id": node_id, **data})
        return methods

    def get_evidence_for_method(self, method_id: str) -> List[Dict[str, Any]]:
        """
        Get all evidence bundle nodes linked to a method.
        """
        bundles = []
        if not self._graph.has_node(method_id):
            return bundles

        candidates = set(self._graph.successors(method_id)).union(self._graph.predecessors(method_id))
        for neighbor in candidates:
            data = self._graph.nodes[neighbor]
            if data.get("node_type") == "EvidenceBundle":
                bundles.append({"node_id": neighbor, **data})

        for node_id, data in self._graph.nodes(data=True):
            if data.get("node_type") == "EvidenceBundle":
                meta = data.get("metadata", {})
                if meta.get("method_id") == method_id:
                    if not any(b["node_id"] == node_id for b in bundles):
                        bundles.append({"node_id": node_id, **data})

        return bundles
