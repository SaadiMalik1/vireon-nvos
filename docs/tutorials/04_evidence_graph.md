# VIREON Tutorial 04: Evidence Graph & Scientific Queries

Discover how to interact with the SQLite-persisted Evidence Graph, query algorithm readiness (SRL), search for benchmark performance, and track scientific provenance.

## Setting Up Evidence Graph & Engine

```python
from vireon_evidence.graph.core import EvidenceGraph
from vireon_evidence.queries.query_engine import ScientificQueryEngine
from vireon_evidence.queries.leaderboard import ScientificLeaderboard, LeaderboardCategory

# Connect to graph
graph = EvidenceGraph(db_path="evidence_graph.db")
query_engine = ScientificQueryEngine(graph)

# Query methods evaluated on PhysioNet with CCC >= 0.99
matches = query_engine.query_methods_by_dataset_and_metric("physionet_motor_imagery", min_ccc=0.99)
for match in matches:
    print(f"Algorithm: {match['method']} | CCC: {match['ccc']:.4f} | Hash: {match['hash']}")

# Generate Scientific Leaderboard
leaderboard = ScientificLeaderboard(graph)
rankings = leaderboard.generate(category=LeaderboardCategory.HIGHEST_CONFIDENCE)
for r in rankings:
    print(f"Rank {r['rank']}: {r['method']} (CCC={r['ccc']:.4f})")
```
