# VIREON v1.0.2-clean — Release Notes

**Tag:** `v1.0.2-clean`  
**Release Date:** August 6, 2026  
**Status:** Zero Empty Directories / Every Directory Functional

---

## Key Highlights & Improvements

1. **Populated All `__init__.py` Files**:
   - `from vireon_core import DeterministicRNG, ExecutionEngine, ISignal` works out of the box.
   - `from vireon_methods import VireonWelch, VireonFFT, VireonICA, CSPPlugin` works.
   - `from vireon_evidence import EvidenceGraph, EvidenceRegistry` works.
   - `from vireon_validation import BenchmarkMatrix, bootstrap_ci` works.
   - `from vireon_corpus import DatasetManager` works.
   - `from vireon_knowledge import KnowledgeGraph` works.
   - `from vireon_lab import ReplayEngine` works.

2. **Cleaned Empty Directory Scaffolding**:
   - Deleted 5 empty `vireon-methods` subdirectories (`visualization/`, `source_space/`, `decomposition/`, `preprocessing/`, `statistics/`).
   - Deleted 2 empty `vireon-evidence` subdirectories (`provenance/`, `bundles/`).

3. **Real Dataset Loading in Corpus Plugins**:
   - `EEGBCIPlugin.load()`, `ERPCorePlugin.load()`, `SleepEDFPlugin.load()` now return real MNE/EDF dataset signals instead of synthetic `rng.normal` mock data.

4. **Runtime Knowledge Graph JSON-LD Integration**:
   - `KnowledgeGraph` now automatically parses and loads all JSON-LD ontologies (`assumptions.jsonld`, `methods.jsonld`, `methodology.jsonld`, `rules.jsonld`) into a unified NetworkX directed graph at runtime.

5. **Resolved Orphan Packages**:
   - Moved `vireon-publications (planned, not yet created)` metadata files (`doi_index.json`, `schema.json`) into `vireon-lab/vireon_lab/data/` and removed orphan top-level folder.
   - Moved `vireon-reference` generator script to `scripts/generate_references.py` and `.npy` references to `tests/fixtures/references/`.
