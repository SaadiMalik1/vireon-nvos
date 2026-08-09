# System Architecture Handbook

## 1. Overview
VIREON is structured as a capability-based orchestration engine. The architecture is explicitly decoupled to separate scientific intent from engineering implementation.

## 2. Core Subsystems
- **vireon-core**: The frozen execution kernel. Handles lifecycle routing, security boundaries, and telemetry generation.
- **vireon-models**: Contains the parameterized digital twins of subjects and hardware measurement chains.
- **vireon-validation**: Responsible for generating empirical evidence bundles that prove the reproducibility of experiments.
- **vireon-knowledge**: A semantic reasoning engine powered by JSON-LD and formal validation rules that enforces scientific constraints.

## 3. Data Flow
1. An `IExperimentDef` defines a scenario.
2. The `ExecutionEngine` instantiates the scenario and dynamically discovers required `IPlugin` modules.
3. The `KnowledgeGraph` validates that the plugins are scientifically compatible with the scenario constraints.
4. Measurements are taken and passed into the `EvidenceGenerator`.
5. An immutable evidence bundle is produced with checksums for every component.

## 4. Design Principles
- **Validation, not Simulation**: We do not simulate brain activity for discovery; we validate software against known physiological envelopes.
- **Contract-first Execution**: Algorithms cannot execute if they violate biological or physical constraints mapped in the Knowledge Graph.
- **Immutability**: Once an experiment completes, its evidence bundle is cryptographically hashed and cannot be altered.


## Phase E Implementation Status

> [!NOTE]
> **Status: Complete (v1.0.3)**
>
> Architecture as documented is implemented across the 10 vireon-* packages.
> ADRs (docs/adr/) are up-to-date with the codebase.