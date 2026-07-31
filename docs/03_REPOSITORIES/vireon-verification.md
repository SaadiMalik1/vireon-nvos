# vireon-verification

`vireon-verification` ensures the absolute mathematical correctness of the system.

## Benchmarks vs. Regression
Unlike `vireon-validation` (which asks scientific questions like "Does this decoder work with 20% impedance drift?"), `vireon-verification` runs CI/CD tests to ensure the code *compiles* and math functions correctly against `vireon-reference`. It establishes SRL-1 to SRL-3.

## Status
- **SRL-1 to SRL-3 CI/CD**: [FULLY IMPLEMENTED] - Deterministic hashing and numerical equivalency tests are active.
- **Automated Formal Verification**: [STUBBED] - Z3 theorem prover integration for proving contract bounds is currently a stub.