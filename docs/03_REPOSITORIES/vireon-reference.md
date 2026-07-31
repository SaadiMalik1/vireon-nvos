# vireon-reference

`vireon-reference` contains unoptimized, mathematically pure implementations of algorithms.

## Purpose
When a developer writes a highly optimized C++ or Rust extension for a signal processing algorithm (to run at scale), they must prove that their optimizations did not introduce numerical drift. 
This repository contains the ground-truth Python/NumPy implementations used exclusively for `vireon-verification` regression testing. It is never used in production pipelines due to its slow execution speed.

## Status
- **DSP Ground Truths**: [FULLY IMPLEMENTED] - Simple reference implementations for Welch, FFT, and IIR exist.
- **Spatial/ML Ground Truths**: [STUBBED] - Reference implementations for CSP, ICA, and Riemannian geometry are pending.