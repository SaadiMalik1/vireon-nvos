# Architecture Book

## System Overview
VIREON is fundamentally structured around a capability-based plugin architecture. Traditional scientific software is often heavily coupled, with monolithic classes representing entire experiments. VIREON decouples the *intent* of a scientific operation from its *implementation*.

### Core Components
1. **The Kernel (`vireon-core`):** The orchestration layer. It manages the Knowledge Graph, the Evidence Engine, and the execution DAG. It never implements scientific logic itself.
2. **The `IPlugin` Interface:** The root contract. Any methodology, model, or artifact generator must implement this to be loaded into the system.
3. **The `IScientificObject` Interface:** The fundamental data carrier. Data is never passed as raw arrays. It is wrapped in objects (like `ISignal` or `IMeasurement`) that track spatial, temporal, and provenance metadata.

## The Plugin Architecture
Every scientific tool in VIREON is a plugin.
Plugins declare:
- **Capabilities:** e.g., "I can estimate power spectral density."
- **Scientific Contracts:** Explicit mathematical, statistical, and numerical assumptions required for the plugin to function without generating erroneous results.

## Data Flow vs. Evidence Flow
### Data Flow
`IScientificObject` payloads flow through a Directed Acyclic Graph (DAG) of plugins. The execution engine enforces type constraints and capabilities.

### Evidence Flow
As data flows, the **Evidence Engine** constructs a shadow graph. It records the state of the digital twin, the specific versions of the plugins used, the explicit assumptions made, and the numerical tolerances observed. This results in an `IEvidence` bundle—an immutable record of exactly *why* a particular scientific outcome was reached.


## Phase E Implementation Status
> [!NOTE]
