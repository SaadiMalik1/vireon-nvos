# ADR 0001: Validation Not Simulation

**Date:** 2026-07-30
**Status:** Accepted

## Context
A major challenge in neurotechnology development is proving that software (like decoders) will work on real human subjects before invasive implantation. Traditionally, developers have relied on "simulation"—attempting to build physiologically perfect computational models of the brain to test their algorithms. 

However, perfect physiological simulation is computationally intractable and philosophically impossible due to the sheer complexity of the central nervous system. When simulations inevitably diverge from reality, decoders trained on them fail catastensively in vivo.

## Decision
We mandate that VIREON is a **Validation** system, not a **Simulation** system. 

Instead of attempting to recreate a perfect brain, VIREON intentionally generates *Adversarial Digital Twins*. We inject precise, mathematically bounded noise, artifacts, and physiological distortions (e.g., stochastic clock jitter, impedance drift, ocular blinks) to stress-test the boundaries of neurotechnology.

## Consequences
- **Positive:** We are not bottlenecked by the impossibility of perfect physiological simulation.
- **Positive:** Decoders validated on VIREON are robust to realistic hardware and physiological failure modes.
- **Negative:** Users expecting a "plug-and-play virtual brain" may find the adversarial nature of the system jarring. 
- **Requirement:** Every generated artifact must be mathematically quantifiable and explicitly declared in a `ScientificContract`.
