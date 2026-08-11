# VIREON × MOABB Integration

This package (`vireon-moabb`) provides the validation and evidence layer for MOABB workflows, as defined in ADR 0008.

## Overview
VIREON no longer attempts to replace MOABB. Instead, it wraps MOABB with cryptographic evidence generation, robustness analysis, and rigorous statistical testing.

## Components
- `adapters`: Provides uniform execution of library code.
- `datasets`: Registers MOABB datasets.
- `robustness`: Evaluates pipeline resilience via perturbations.
- `statistics`: Computes confidence intervals and significance.
- `evidence`: Cryptographically secures execution traces.
