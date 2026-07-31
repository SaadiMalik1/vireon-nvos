# ADR 0003: Scientific Contracts

**Date:** 2026-07-30
**Status:** Accepted

## Context
"Garbage In, Garbage Out" is the cardinal sin of scientific computing. Frequently, algorithms are applied to data that violate their mathematical assumptions (e.g., using Independent Component Analysis on highly non-stationary data, or computing Welch's PSD on a transient signal). Standard type-checking (e.g., ensuring an argument is a `float` or a `numpy.ndarray`) is insufficient to catch scientific errors.

## Decision
Every `IPlugin` must define a `ScientificContract`. This contract explicitly lists the mathematical, statistical, numerical, and hardware assumptions required for the plugin's output to be valid. The contract must also define the failure conditions and the expected numerical tolerances.

## Consequences
- **Positive:** Prevents the silent propagation of scientific errors.
- **Positive:** Automatically generates documentation for the boundaries of an algorithm.
- **Negative:** Forces researchers to rigorously mathematically justify their code before it can be run in the ecosystem.
- **Requirement:** The `EvidenceEngine` must dynamically verify that the metadata of the `IScientificObject` payload satisfies the downstream plugin's contract before execution is permitted.


## Phase E Implementation Status
> [!NOTE]
> As of Phase E, the architecture has expanded to include Massive Campaigns, Hardware Digital Twins, EvidenceBundle v5 (SRI/Regulatory mapping), and the Reproduce CLI. Features described in this document may be subject to these new workflows. If specific API endpoints, models, or UI components are discussed but missing in the codebase, they are currently [STUBBED] pending Phase F implementation.
