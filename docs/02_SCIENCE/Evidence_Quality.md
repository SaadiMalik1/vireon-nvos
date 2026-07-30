# Evidence Quality

The output of a VIREON execution is an `IEvidence` bundle. The quality of this evidence is ranked by the Scientific Readiness Level (SRL).

## Regulatory Grade Evidence (SRL-9)
For an `IEvidence` bundle to be submitted to a regulatory body (e.g., FDA), it must:
1. Be cryptographically signed by the Evidence Engine.
2. Rely strictly on `IPlugin` nodes that have achieved at least SRL-5 (Empirical Validation).
3. Demonstrate robust calibration of Bayesian Uncertainty.
4. Supply a fully reproducible JSON-LD graph linking every assumption to peer-reviewed literature in the `vireon-knowledge` graph.