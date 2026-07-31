# vireon-knowledge

`vireon-knowledge` is the semantic ontology of the neurotechnology domain.

## The Problem with Strings
In standard Python, an assumption like `"Wide-Sense Stationarity"` is just a string. The Python runtime cannot deduce that an `ElectrodePop` (a transient artifact) violates this assumption.

## The Ontology
This repository maintains a Graph (currently serialized as JSON-LD) that maps the universe of constraints.

### Node Types
- **`vk:Method`**: E.g., Welch PSD, Independent Component Analysis.
- **`vk:Assumption`**: E.g., Ergodicity, Additive Noise, Linear Superposition.
- **`vk:Artifact`**: E.g., Ocular Blink, EMG Burst.
- **`vk:Paper`**: DOI links to canonical literature.

### Edges
The graph connects these nodes:
- `vk:Method:Welch` **REQUIRES** `vk:Assumption:Stationarity`
- `vk:Artifact:ElectrodePop` **VIOLATES** `vk:Assumption:Stationarity`

The `vireon-core` Evidence Engine queries this graph at runtime. If a data payload containing an `ElectrodePop` attempts to enter the `Welch PSD` plugin, the kernel will halt execution and throw a `ScientificContractViolation`.

- **Status**: [PARTIALLY IMPLEMENTED (WIP)] - The JSON-LD schemas and Evidence Bundle v5 ontology exist. However, the active query engine (`KnowledgeQueryEngine`) that performs inference across the ontology has been migrated to `vireon-evidence` and is still a stub.

## Phase E Implementation Status
> [!NOTE]
> As of Phase E, the architecture has expanded to include Massive Campaigns, Hardware Digital Twins, EvidenceBundle v5 (SRI/Regulatory mapping), and the Reproduce CLI. Features described in this document may be subject to these new workflows. If specific API endpoints, models, or UI components are discussed but missing in the codebase, they are currently [STUBBED] pending Phase F implementation.
