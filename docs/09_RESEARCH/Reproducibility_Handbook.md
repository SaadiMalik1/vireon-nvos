# Reproducibility Handbook

## 1. The Bundle Standard
Every experiment run by VIREON must output an evidence bundle containing:
- `manifest.json`: Scenario parameters.
- `events.json`: The causal event log.
- `measurements.json`: Derived metrics.
- `environment.json`: Versions of the OS, Python, and loaded libraries.
- `telemetry.npz` (or parquet): The bit-exact signal output.
- `hashes.json`: SHA-256 integrity checksums.

## 2. CI/CD Requirements
All plugins must be tested deterministically in CI/CD. The `ExecutionEngine.run` method accepts a `seed` argument that guarantees the PRNG state will yield identical outcomes across hardware.

## 3. Discrepancy Resolution
If numerical discrepancies exist between VIREON and reference packages (e.g. EEGLAB), the source of the discrepancy must be documented mathematically in the Knowledge Graph constraints.
