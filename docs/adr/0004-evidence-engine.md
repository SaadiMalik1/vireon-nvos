# ADR 0004: Evidence Engine

**Date:** 2026-07-30
**Status:** Accepted

## Context
When a commercial BCI company submits validation data to a regulatory body, or an academic lab publishes a paper, the final output is usually a PDF or a static CSV file. The provenance of that data—the exact sequence of steps, code versions, and mathematical assumptions used to generate it—is lost.

## Decision
VIREON will implement an `EvidenceEngine`. As `IScientificObject` payloads traverse the plugin execution DAG, the `EvidenceEngine` will shadow the execution. It intercepts every node execution to record the inputs, the output, the active `ScientificContract`, the random seeds used, and the git hash of the plugin. 

## Consequences
- **Positive:** Automatically generates regulatory-grade, immutable `IEvidence` bundles that can be independently audited.
- **Positive:** Solves the reproducibility crisis for any experiment run within VIREON.
- **Negative:** Slight performance overhead during execution as provenance metadata is serialized.
- **Requirement:** All inputs and outputs to plugins must be strictly typed as subclasses of `IScientificObject` to allow metadata tracking.
