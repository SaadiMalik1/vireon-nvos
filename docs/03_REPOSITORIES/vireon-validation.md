# vireon-validation

## Statistical Rigor

The math library behind VIREON's evidence generation. It contains the implementations for computing Concordance Correlation Coefficient (CCC), Signal-to-Distortion Ratio (SDR), Bland-Altman statistics, and other rigorous metrics necessary for determining empirical agreement between methods and baselines.

## Integration in Phase E
This repository is integrated into the VIREON scientific ecosystem (see docs/STATUS.md for current implementation status). It supports the generation of verifiable EvidenceBundles and contributes directly to the semantic tracking in the Evidence Graph. All methods are dynamically orchestrated through the Cartesian Benchmark Matrix, ensuring reproducibility and cryptographically assured provenance.
