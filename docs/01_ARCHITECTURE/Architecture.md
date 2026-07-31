# Architecture Overview

The VIREON NVOS (Neurotechnology Validation Operating System) architecture has evolved from a simple algorithmic benchmarking suite into a comprehensive, layered infrastructure designed to generate, organize, and independently reproduce computational neuroscience evidence.

## The 6-Layer Vision

The architecture is divided into six progressive layers:

1. **Layer 1: Scientific Corpus** (`vireon-knowledge`, `Datasets`)
   Contains datasets, BIDS ingestion structures, metadata, and the provenance tracking necessary to root analyses in physical reality.

2. **Layer 2: Computational Methods** (`vireon-methods`, `vireon-models`)
   Contains reference wrappers and native implementations of algorithms (filtering, spatial, connectivity, source imaging).

3. **Layer 3: Evidence Generation Platform** (`vireon-core`, `vireon-validation`)
   The core engine driving benchmarking campaigns, computing statistical equivalences, and packaging results into immutable `EvidenceBundle` artifacts.

4. **Layer 4: Scientific Knowledge Graph** (`vireon-evidence`)
   The semantic ontology mapping Methods, Datasets, Claims, Clinical Domains, and **Workflows**. It acts as the queryable truth base for operational envelopes and failure modes. It includes a robust Knowledge Query API for semantic evidence discovery.

5. **Layer 5: Reproducibility Platform** (`vireon-lab`)
   Provides the ability to execute massive factorial campaigns, launch digital twins, and expose the `vireon reproduce DOI` CLI, allowing anyone to replicate full papers effortlessly with calculated Scientific Reproducibility Indexes (SRI).

6. **Layer 6: Neurotechnology Validation OS**
   The final synthesis. At this layer, VIREON operates not merely as a library, but as a continuous validation infrastructure monitoring the limits, reliability, and clinical readiness of complete neurotechnology pipelines, mapping natively to regulatory standards (FDA, ISO, IEC).

## Phase E Implementation Status
> [!NOTE]
> As of Phase E, the architecture has expanded to include Massive Campaigns, Hardware Digital Twins, EvidenceBundle v5 (SRI/Regulatory mapping), and the Reproduce CLI. Features described in this document may be subject to these new workflows. If specific API endpoints, models, or UI components are discussed but missing in the codebase, they are currently [STUBBED] pending Phase F implementation.
