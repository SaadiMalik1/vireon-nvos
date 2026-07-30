# Benchmarking

Benchmarking in VIREON is the automated execution of Validation scenarios.

## Execution
Benchmarks are defined in YAML manifests within `vireon-validation`. They specify:
1. The target plugin (e.g., `WelchPSD`).
2. The dataset or generative twin.
3. The expected metric (e.g., `RMSE`).
4. The maximum allowed tolerance (e.g., `1e-6`).

These benchmarks are executed continuously via `vireon-verification` CI pipelines to ensure that scientific accuracy does not regress as the codebase evolves.