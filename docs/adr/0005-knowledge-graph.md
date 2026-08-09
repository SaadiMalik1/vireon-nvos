# ADR 0005: Knowledge Graph

**Date:** 2026-07-30
**Status:** Accepted

## Context
When a `ScientificContract` declares that it assumes "Wide-Sense Stationarity", that string is semantically meaningless to a standard python runtime. Without a semantic mapping, the system cannot deduce that a transient event (like an electrode pop) violates Wide-Sense Stationarity.

## Decision
VIREON will utilize a formal ontological **Knowledge Graph** (`vireon-knowledge`). This graph explicitly encodes the relationships between Methods, Assumptions, Artifacts, Diseases, and Literature. 
For example: `[vk:Artifact:ElectrodePop] -> (VIOLATES) -> [vk:Assumption:Stationarity]`.

## Consequences
- **Positive:** Enables intelligent constraint solving and automated experimental design validation.
- **Positive:** Connects abstract code directly to canonical scientific literature (e.g. `[vk:Method:Welch] -> (IMPLEMENTS) -> [vk:Paper:Welch1967]`).
- **Negative:** Maintaining the ontology requires domain expertise and constant updating as neurotechnology evolves.
- **Requirement:** The graph must be queryable by the `EvidenceEngine` at runtime to resolve complex dependency trees.


## Phase E Implementation Status

> [!NOTE]
> **Status: Accepted & Implemented (v1.0.3)**
>
> Architectural Decision Record validated against core codebase.