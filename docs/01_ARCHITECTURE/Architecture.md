# Architecture Overview

The VIREON NVOS architecture is designed to enforce maximum decoupling between scientific intent and execution logic.

## The Tripartite Structure

The architecture is divided into three distinct conceptual zones:

1. **The Core Engine (`vireon-core`)**: The dumb orchestrator. It knows nothing about brains, signals, or physics. It only knows how to match capabilities, validate JSON-LD contracts, and route payloads through a DAG.
2. **The Knowledge Graph (`vireon-knowledge`)**: The semantic ontology. It holds the fundamental truths of the ecosystem (e.g., "Ocular Blinks occur in the frontal cortex", "Welch PSD requires Stationarity").
3. **The Plugin Ecosystem (`vireon-models`, `vireon-methods`)**: The actual science. These repositories contain the executable code that generates artifacts, models dipoles, or extracts features.

By isolating the scientific logic in the Plugin Ecosystem, we ensure that the Core Engine remains highly stable, while researchers can rapidly iterate on new models without risking regressions in the orchestration logic.