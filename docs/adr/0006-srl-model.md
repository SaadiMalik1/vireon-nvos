# ADR 0006: Scientific Readiness Level (SRL) Model

**Date:** 2026-07-30
**Status:** Accepted

## Context
Not all code in a research repository is equally trustworthy. A newly implemented artifact generator might compile and run without throwing errors, but it might lack any physiological justification. Users need a metric to trust the components they include in their execution DAGs.

## Decision
We adopt the **Scientific Readiness Level (SRL)** metric (0 through 9), inspired by NASA's Technology Readiness Levels (TRL). 
- SRL-1 implies mathematical justification. 
- SRL-3 implies cross-validation against standard tools (e.g., SciPy).
- SRL-9 implies regulatory-grade evidence with multi-lab consensus.
Every plugin must declare its SRL.

## Consequences
- **Positive:** Provides immediate, standardized communication regarding the maturity of a tool or model.
- **Positive:** Allows researchers to filter validation pipelines to only use high-SRL components when generating evidence for regulatory submissions.
- **Negative:** Assigning an SRL is partially subjective until strict automated criteria are fully implemented.
- **Requirement:** `task.md` and Contributor Guides must mandate empirical validation for promotion to higher SRL tiers.


## Phase E Implementation Status
> [!NOTE]
> As of Phase E, the architecture has expanded to include Massive Campaigns, Hardware Digital Twins, EvidenceBundle v5 (SRI/Regulatory mapping), and the Reproduce CLI. Features described in this document may be subject to these new workflows. If specific API endpoints, models, or UI components are discussed but missing in the codebase, they are currently [STUBBED] pending Phase F implementation.
