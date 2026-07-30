# ADR 0002: Plugin-First Kernel

**Date:** 2026-07-30
**Status:** Accepted

## Context
Neurotechnology research code often devolves into massive "God classes" (e.g., `ExperimentRunner` or `EEGSimulator`) where data loading, preprocessing, signal extraction, and statistical testing are tightly coupled. This makes code reuse impossible and independent validation exceptionally difficult.

## Decision
The VIREON kernel (`vireon-core`) will contain zero scientific logic. Instead, it will act strictly as a capability-based router. Every piece of scientific logic—whether it is a noise generator, a forward model, or a power spectral density estimator—must be instantiated as an `IPlugin`. 

## Consequences
- **Positive:** Maximum decoupling. A developer building a new artifact model does not need to understand how the core engine works.
- **Positive:** Enables arbitrary Directed Acyclic Graphs (DAGs) of execution.
- **Negative:** Increased boilerplate. Every script must be wrapped in a plugin class and explicitly declare its capabilities.
- **Requirement:** A robust reflection and plugin discovery mechanism must be maintained in `vireon-core`.
