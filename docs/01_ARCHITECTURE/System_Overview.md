# System Overview

A high-level view of how a standard VIREON execution run unfolds.

## The Execution Lifecycle

1. **Goal Declaration:** The user defines a YAML manifest specifying the desired target metric (e.g., `Estimate Motor Imagery Decoder Accuracy`).
2. **Graph Resolution:** The `vireon-core` engine parses the manifest and resolves a sequence of plugins that can transform a raw empirical dataset or synthetic generator into the requested metric.
3. **Contract Verification:** Before execution begins, the `EvidenceEngine` queries the `vireon-knowledge` graph to ensure that the cumulative assumptions of the DAG do not conflict.
4. **Data Flow:** `IScientificObject` payloads (like `ISignal` and `IMeasurement`) are passed sequentially through the plugin instances.
5. **Evidence Generation:** As each node completes, its inputs, outputs, Git hashes, and stochastic states are serialized into the `IEvidence` bundle.
6. **Output:** The system yields both the final numerical result and the immutable JSON-LD provenance bundle.