# vireon-evidence

`vireon-evidence` handles the serialization, ontological mapping, and querying of scientific evidence generated across the ecosystem. (Note: Originally this functionality was bundled in `vireon-knowledge`, but it has been refactored into its own dedicated platform repository).

## The Graph & Ontology
This repository maintains the Knowledge Graph (currently serialized as JSON-LD, intended for an RDF triplestore) that maps the universe of constraints.

### Node Types
- **`vk:Method`**: E.g., Welch PSD, Independent Component Analysis.
- **`vk:Assumption`**: E.g., Ergodicity, Additive Noise, Linear Superposition.
- **`vk:Artifact`**: E.g., Ocular Blink, EMG Burst.
- **`vk:Paper`**: DOI links to canonical literature.

## Evidence Bundle v5
`vireon-evidence` defines the core schema for the `IEvidence` bundle.
- **Status**: [FULLY IMPLEMENTED] 
- Support for `Regulatory Profiles` (FDA, ISO) and the `Scientific Reproducibility Index (SRI)` are active and enforce strict structural integrity via hashes.

## Knowledge Infrastructure Query API
- **Status**: [PARTIALLY IMPLEMENTED (WIP)]
- A `KnowledgeQueryEngine` exists for basic semantic querying (e.g., finding all datasets that support Motor Imagery).
- Advanced logical inference and cross-domain ontological reasoning are currently stubbed and pending future triplestore integration.

## Failure Atlas
- **Status**: [STUBBED]
- The schema for the `Failure Atlas` (recording the absolute boundary conditions where algorithms fail) is defined, but the pipeline automatically routing massive campaign failures into this atlas is still under active development.
