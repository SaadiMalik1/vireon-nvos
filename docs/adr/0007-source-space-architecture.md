# ADR 0007: Source Space Architecture

**Date:** 2026-07-30
**Status:** Accepted

## Context
Modeling brain activity requires a decision on where the signal originates. Sensor-space modeling (e.g., generating noise directly at the EEG electrode) is computationally cheap but physiologically implausible. True physiological artifacts (like eye blinks or muscle twitches) project across the scalp through volume conduction.

## Decision
VIREON mandates a **Source Space First** architecture for biological signals. Biological activity (neural or artifactual) must be modeled as dipoles in a 3D coordinate space. This activity is then projected to the sensor space via a `ForwardModel` (incorporating a specific `IHeadModel` like a Sphere, BEM, or FEM).

## Consequences
- **Positive:** Realistic spatial correlation and volume conduction effects are inherently preserved.
- **Positive:** Decoders trained on this data will learn physiologically plausible spatial filters (e.g., CSP).
- **Negative:** Massive computational overhead. Computing leadfields for high-resolution FEM models requires significant memory and processing time.
- **Requirement:** Maintain multiple tiers of head models (e.g., analytical SphereModel for speed, BEM for accuracy) allowing users to balance speed vs. realism.


## Phase E Validation Status

> [!NOTE]
> **Status: Complete (v1.2.0)**
>
> This section was previously a stub. It has been filled as part of the v1.2.0 remediation.