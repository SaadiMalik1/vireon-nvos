# vireon-methods

## Algorithmic Contracts

Houses the `IPlugin` interface and Scientific Contracts. Every method inside `vireon-methods` must explicitly declare its mathematical assumptions, its dependencies, and the academic literature it originates from. This forces algorithmic implementations to become scientifically bound, traceable entities rather than arbitrary code.

## Integration in Phase E
This repository is integrated into the VIREON scientific ecosystem (see docs/STATUS.md for current implementation status). It supports the generation of verifiable EvidenceBundles and contributes directly to the semantic tracking in the Evidence Graph. All methods are dynamically orchestrated through the Cartesian Benchmark Matrix, ensuring reproducibility and cryptographically assured provenance.
