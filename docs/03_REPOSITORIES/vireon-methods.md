# vireon-methods (DEPRECATED)

## Algorithmic Contracts

> [!WARNING]
> This repository is deprecated as of v2.0.0 (MOABB Integration). All algorithmic implementations have been moved to `vireon-moabb` and MOABB's native paradigms. The legacy native implementations are maintained for backwards compatibility in `vireon_methods/reference/deprecated`.

Houses the `IPlugin` interface and Scientific Contracts. Every method inside `vireon-methods` explicitly declared its mathematical assumptions, its dependencies, and the academic literature it originated from. This forced algorithmic implementations to become scientifically bound, traceable entities rather than arbitrary code.

## Integration in Phase E
This repository was integrated into the VIREON scientific ecosystem (see docs/STATUS.md for current implementation status). It supported the generation of verifiable EvidenceBundles and contributed directly to the semantic tracking in the Evidence Graph. All methods were dynamically orchestrated through the Cartesian Benchmark Matrix, ensuring reproducibility and cryptographically assured provenance.
