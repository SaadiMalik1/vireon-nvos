# Regression & CI/CD

Scientific software must not silently degrade. The `vireon-verification` repository ensures that the math is always correct.

## The Verification Suite
Every pull request to `vireon-methods` or `vireon-models` triggers a comprehensive suite of numerical regression tests via GitHub Actions.

### Tolerance Bounds
We do not test for boolean equality (`True`/`False`), as floating-point arithmetic across different architectures (e.g., Apple Silicon vs x86) will diverge. Instead, we test against the unoptimized ground-truth in `vireon-reference` using strict tolerances (e.g., `np.allclose(result, reference, rtol=1e-5)`).

### Fuzzing
Inputs are fuzzed with `NaN`s, `Inf`s, and extreme scaling factors to ensure that `IPlugins` fail gracefully and throw appropriately typed `ScientificContractViolations` rather than crashing the execution DAG.


## Phase E Validation Status

> [!NOTE]
> **Status: Complete (v1.2.0)**
>
> This section was previously a stub. It has been filled as part of the v1.2.0 remediation.