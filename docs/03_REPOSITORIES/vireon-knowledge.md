# vireon-knowledge

`vireon-knowledge` is the semantic ontology of the neurotechnology domain.

## The Problem with Strings
In standard Python, an assumption like `"Wide-Sense Stationarity"` is just a string. The Python runtime cannot deduce that an `ElectrodePop` (a transient artifact) violates this assumption.

## The Ontology
This repository maintains a Graph (currently serialized as JSON-LD, intended for an RDF triplestore) that maps the universe of constraints.

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