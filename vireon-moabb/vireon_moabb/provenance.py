import networkx as nx
import json
from typing import Any

class ProvenanceGraph:
    """NetworkX directed acyclic graph for evidence provenance."""

    def __init__(self):
        self.graph = nx.DiGraph()

    def add_node(self, node_id: str, metadata: dict[str, Any]):
        """Add a node (dataset, operation, trace, bundle) to the graph."""
        self.graph.add_node(node_id, **metadata)

    def add_edge(self, source_id: str, target_id: str, relationship: str):
        """Add an edge defining the provenance relationship."""
        self.graph.add_edge(source_id, target_id, relationship=relationship)

    def to_json(self) -> str:
        """Export graph to JSON for the evidence bundle."""
        data = nx.node_link_data(self.graph)
        return json.dumps(data, indent=2, default=str)

    def generate_dot(self) -> str:
        """Generate Graphviz DOT format for rendering."""
        try:
            from networkx.drawing.nx_pydot import to_pydot
            pydot_graph = to_pydot(self.graph)
            return pydot_graph.to_string()
        except ImportError:
            return "// pydot not installed"
