# vireon-corpus

## Dataset Registry

The central nervous system for biological dataset management in VIREON. It handles the parsing, caching, and streaming of standardized data formats (e.g., BIDS, PhysioNet EDF) into the core pipeline. It abstracts away the intricacies of multi-modal neuro-data parsing so the benchmark matrix can uniformly inject perturbations.

## Integration in Phase E
This repository is integrated into the VIREON scientific ecosystem (see docs/STATUS.md for current implementation status). It supports the generation of verifiable EvidenceBundles and contributes directly to the semantic tracking in the Evidence Graph. All methods are dynamically orchestrated through the Cartesian Benchmark Matrix, ensuring reproducibility and cryptographically assured provenance.
