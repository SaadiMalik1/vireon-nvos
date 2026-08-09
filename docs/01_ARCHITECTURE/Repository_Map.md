# Repository Map

The VIREON ecosystem is intentionally fragmented into domain-specific repositories to enforce decoupling.

## The Kernel
- **`vireon-core`**: The execution DAG, capability router, and Evidence Engine. Contains the core `EvidenceBundle v5` schemas tracking SRI and Regulatory Profiles.

## The Ontology & Knowledge
- **`vireon-knowledge`**: The formal ontology and Knowledge Graph linking methods, assumptions, and literature.
- **`vireon-evidence`**: Contains the Knowledge Infrastructure Query API (`vireon_evidence.graph.query`) and the `Failure Atlas` for tracking operational envelopes.

## The Science
- **`vireon-models`**: Generative digital twins (Artifacts, Head models, Source space). Specifically expanded to include Hardware Digital Twins (`AmplifierTwin`, `TelemetryTwin`, `BatteryDegradationTwin`).
- **`vireon-methods`**: Signal processing and statistical methodologies (e.g., Welch PSD, CSP).

## Validation & Testing
- **`vireon-validation`**: Automated benchmarking scenarios, Massive Campaign Orchestrators, and the `vireon_validation.statistics.framework` covering Bland-Altman, ICC, and KS statistics.
- **`vireon-verification`**: Continuous Integration checks ensuring standard mathematical and numerical agreements.

## Data & Evidence
- **`vireon-corpus`**: High-quality, curated, and fingerprinted physiological datasets.
- **`vireon-publications`**: Executable evidence graphs reproducing the results of canonical papers.
- **`vireon-reference`**: Ground-truth implementations (often slow, unoptimized Python) used to verify faster rust/C++ extensions.
- **`vireon-lab`**: Interactive Jupyter notebooks and the `vireon reproduce [DOI]` CLI for one-command paper replication.

## Phase E Implementation Status

> [!NOTE]
> **Status: Complete (v1.0.3)**
>
> Architecture as documented is implemented across the 10 vireon-* packages.
> ADRs (docs/adr/) are up-to-date with the codebase.