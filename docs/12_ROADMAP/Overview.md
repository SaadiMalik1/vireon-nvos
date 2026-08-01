# Roadmap to SRL-9

Our primary objective is to transition VIREON from an academic validation framework into a recognized regulatory standard.

## 2026 Q3: The Knowledge Graph Stabilization
- **`vireon-devices`**: Standardized hardware interface contracts and emulators. `[SPEC]`
- **`vireon-corpus`**: Highly curated, fingerprinted canonical physiological datasets. `[SPEC]`
- **`vireon-knowledge`**: Semantic graph capturing clinical logic and assertions. `[IMPLEMENTED]`
- Map the 50 most common BCI assumptions to canonical literature.

## 2026 Q4: The Validation Corpus
- Ingest and fingerprint 5 high-quality, open-source empirical datasets (e.g., PhysioNet MI, BNCI Horizon).
- Establish the baseline benchmarks for standard decoders (CSP, Riemannian Geometry).

## 2027 Q1: Hardware Digital Twins
- Release SRL-5 validated simulators for the OpenBCI Cyton and the NeuroNexus arrays.

## 2027 Q4: FDA MDDT Submission (Target)
- Submit VIREON to the FDA Medical Device Development Tools program for qualification as a non-clinical assessment model.

## Implementation Status (Current Phase E)

VIREON has progressed past its initial architectural scaffolding into full empirical validation. The framework now natively supports real biological datasets, cartesian benchmark campaigns, and verifiable cryptographic evidence generation.

### Fully Implemented Components
The foundational orchestration and core abstractions are functional:
- **`vireon_core`**: The API capabilities, `IPlugin` contracts, and the `ExecutionEngine` (including `DeterministicRNG` and the Causal Graph).
- **Evidence Engine JSON Schema**: The structure for validating `IEvidence` telemetry.
- **CI/CD Pipeline**: Automated GitHub Actions ensuring environment reproducibility and formatting.

### Fully Implemented Components (Phase E)
- **`vireon-core`**: The API capabilities, `IPlugin` contracts, and the `ExecutionEngine` (including `DeterministicRNG` and the Causal Graph).
- **`vireon-evidence`**: Evidence Engine `MultiFormatReportGenerator` emitting Markdown, Reproducibility Summaries, and Semantic Graphs.
- **`vireon-corpus`**: `PhysioNetMotorImageryProvider` fetching and preprocessing actual EEG BCI data.
- **`vireon-methods`**: Operational signal processing algorithms (`CSPPlugin`) mapped directly to canonical literature (e.g. Ramoser 2000).
- **Cartesian Benchmark Runner**: Generates EvidenceBundles containing statistical bounds and robustness sweeps for the implemented plugins.

### Next Steps (Phase F)
- Expand dataset ingestors to globally distributed BIDS archives.
- Publish `vireon-knowledge` Failure Atlas to a centralized ontology server.
- Introduce formal API bindings for Hardware Digital Twins (e.g., OpenBCI Cyton).


