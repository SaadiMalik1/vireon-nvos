### Acceptance Criteria Checklist
- [x] `leaderboard.generate()` returns methods sorted by real aggregated metrics from the graph.
- [x] `query_engine.query_methods_by_dataset_and_metric()` traverses the graph and evaluates conditions.
- [x] `timeline.generate_timeline()` extracts real temporal events from the graph.
- [x] `meta_analysis.recompute()` computes real DerSimonian-Laird random-effects meta-analysis from bundled results.
- [x] `evidence_service.get_method_profile()` aggregates real benchmark counts, metrics, datasets, and failures.
- [x] `rg "# Stub" vireon-evidence/` returns 0.
- [x] `rg "0\.998|0\.985" vireon-evidence/vireon_evidence/queries/` returns 0.
- [x] All unit tests in `vireon-evidence/tests/` pass.

### Verification Output
`pytest vireon-evidence/tests/` passed (11 passed). No stub comments or hardcoded query returns.
