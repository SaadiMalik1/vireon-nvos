# System Overview

A high-level view of how a standard VIREON execution run unfolds across its advanced validation ecosystem.

## The Execution Lifecycle

1. **Goal Declaration:** The user defines a YAML manifest specifying the desired target metric (e.g., `Estimate Motor Imagery Decoder Accuracy`) or triggers a massive factorial campaign across multiple datasets, perturbations, and hardware models.
2. **Graph Resolution:** The `vireon-core` engine parses the manifest and resolves a sequence of plugins that can transform a raw empirical dataset or synthetic generator into the requested metric. This includes full End-to-End Workflow benchmarking.
3. **Contract Verification:** Before execution begins, the `EvidenceEngine` queries the `vireon-knowledge` graph to ensure that the cumulative assumptions of the DAG do not conflict.
4. **Data Flow & Perturbations:** `IScientificObject` payloads (like `ISignal` and `IMeasurement`) are passed sequentially through the plugin instances. During validation, perturbations (e.g. from `AmplifierTwin` or `TelemetryTwin`) inject mathematically precise noise.
5. **Evidence Generation:** As each node completes, its inputs, outputs, Git hashes, and stochastic states are serialized into the `IEvidence` bundle.
6. **Regulatory Assessment:** The Evidence Bundle v5 maps findings to Regulatory Profiles (FDA GMLP, IEC 62304) and computes the Scientific Reproducibility Index (SRI).
7. **Knowledge Query:** The output is yielded both as a numerical result and committed back to the queryable Knowledge Infrastructure for community discovery.

## Phase E Implementation Status
> [!NOTE]
> As of Phase E, the architecture has expanded to include Massive Campaigns, Hardware Digital Twins, EvidenceBundle v5 (SRI/Regulatory mapping), and the Reproduce CLI. Features described in this document may be subject to these new workflows. If specific API endpoints, models, or UI components are discussed but missing in the codebase, they are currently [STUBBED] pending Phase F implementation.
