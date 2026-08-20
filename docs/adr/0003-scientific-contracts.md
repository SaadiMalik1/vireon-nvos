# ADR 0003: Scientific Contracts

**Date:** 2026-07-30
**Status:** Refined by ADR 0008 (VIREON x MOABB Integration)

## Context
"Garbage In, Garbage Out" is the cardinal sin of scientific computing. Frequently, algorithms are applied to data that violate their mathematical assumptions (e.g., using Independent Component Analysis on highly non-stationary data, or computing Welch's PSD on a transient signal). Standard type-checking (e.g., ensuring an argument is a `float` or a `numpy.ndarray`) is insufficient to catch scientific errors.

## Decision
Every `IPlugin` must define a `ScientificContract`. This contract explicitly lists the mathematical, statistical, numerical, and hardware assumptions required for the plugin's output to be valid. The contract must also define the failure conditions and the expected numerical tolerances.

## Consequences
- **Positive:** Prevents the silent propagation of scientific errors.
- **Positive:** Automatically generates documentation for the boundaries of an algorithm.
- **Negative:** Forces researchers to rigorously mathematically justify their code before it can be run in the ecosystem.
- **Requirement:** The `EvidenceEngine` must dynamically verify that the metadata of the `IScientificObject` payload satisfies the downstream plugin's contract before execution is permitted.


## Phase E Validation Status

> [!NOTE]
> **Status: Complete (v1.2.0)**
>
> This section was previously a stub. It has been filled as part of the v1.2.0 remediation.