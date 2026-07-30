# Roadmap to SRL-9

Our primary objective is to transition VIREON from an academic validation framework into a recognized regulatory standard.

## 2026 Q3: The Knowledge Graph Stabilization
- Finalize the core ontological structure in `vireon-knowledge`.
- Map the 50 most common BCI assumptions to canonical literature.

## 2026 Q4: The Validation Corpus
- Ingest and fingerprint 5 high-quality, open-source empirical datasets (e.g., PhysioNet MI, BNCI Horizon).
- Establish the baseline benchmarks for standard decoders (CSP, Riemannian Geometry).

## 2027 Q1: Hardware Digital Twins
- Release SRL-5 validated simulators for the OpenBCI Cyton and the NeuroNexus arrays.

## 2027 Q4: FDA MDDT Submission (Target)
- Submit VIREON to the FDA Medical Device Development Tools program for qualification as a non-clinical assessment model.

## Implementation Status (Current Prototype)

VIREON is built using a **Documentation-Driven Development (DDD)** methodology. The documentation you are reading defines the long-term system architecture. The actual codebase is currently in its **early scaffolding phase**.

### Fully Implemented Components
The foundational orchestration and core abstractions are functional:
- **`vireon_core`**: The API capabilities, `IPlugin` contracts, and the `ExecutionEngine` (including `DeterministicRNG` and the Causal Graph).
- **Evidence Engine JSON Schema**: The structure for validating `IEvidence` telemetry.
- **CI/CD Pipeline**: Automated GitHub Actions ensuring environment reproducibility and formatting.

### Stubs / Works in Progress
The actual mathematical and computational cores of many plugins are explicitly stubbed (`pass` blocks) as we establish the interface boundaries:
- **Algorithms (`vireon-methods`)**: CSP, Welch, ICA, and Riemannian Geometry are API stubs waiting for their computational core.
- **Verification Tests (`vireon-verification/literature`)**: Tests against canonical literature datasets (e.g., Sleep-EDF, BCI Competition) currently simulate pass conditions and are marked with `@pytest.mark.skip(reason="WIP")`.
- **Benchmark Runner**: Currently only validates YAML schema parsing, not mathematical execution.
- **Datasets**: The dataset repository directories exist as manifests (catalogs) without the underlying large files (to be added via git-lfs or network fetchers).

### Next Steps / What Needs Work
- Implement the actual signal processing math inside the plugin stubs.
- Replace mock literature verification values with real computation pipelines.
- Expand the `BenchmarkRunner` to execute full digital twin pipelines rather than just YAML validation.
