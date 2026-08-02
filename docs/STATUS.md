# VIREON Implementation Status

This document provides an honest, verifiable accounting of the implementation status of all VIREON components and features as of the research prototype (v0.2.0).

## Core Kernel & Architecture
| Component | Status | Details |
|---|---|---|
| Plugin Discovery | IMPLEMENTED | Dynamic entry_points and directory scanning in `vireon_core.kernel.plugins`. |
| DAG Execution Engine | IMPLEMENTED | Dependency resolution via `graphlib.TopologicalSorter` in `ExecutionEngine`. |
| Wire Protocol Decoder | IMPLEMENTED | Zero-copy / structured numpy buffer decoding in `WireDecoder`. |
| Contract Validator | IMPLEMENTED | Raises `ScientificContractViolation` upon invariant failure. |
| Transaction Content Hash | IMPLEMENTED | Cryptographic SHA-256 state hashing over bundles. |
| Environment Capture | IMPLEMENTED | Real CPU, OS, Python version, and dependency capture. |

## Signal Processing & Methods (`vireon-methods`)
| Method | Status | Verification Reference |
|---|---|---|
| Welch PSD | IMPLEMENTED | Verified against `scipy.signal.welch` (tolerance 1e-7). |
| FFT | IMPLEMENTED | Verified against `scipy.fft.rfft` (tolerance 1e-12). |
| STFT | IMPLEMENTED | Verified against `scipy.signal.stft`. |
| Wavelets (CWT) | IMPLEMENTED | Verified against Ricker / Morlet references. |
| FastICA | IMPLEMENTED | Verified against `sklearn.decomposition.FastICA`. |
| CSP | IMPLEMENTED | Verified against `mne.decoding.CSP`. |
| FIR / IIR Filters | IMPLEMENTED | Verified against `scipy.signal` filter design. |
| LCMV Beamforming | IMPLEMENTED | Real unit gain LCMV spatial filter. |
| Source Localization | IMPLEMENTED | Real dipole forward and inverse solvers. |
| Connectivity & wPLI | IMPLEMENTED | Real phase lag index and weighted PLI estimators. |
| Surface Laplacian / REST | IMPLEMENTED | Spherical spline surface Laplacian. |

## Validation & Biostatistics (`vireon-validation`)
| Tool | Status | Details |
|---|---|---|
| Bland-Altman | IMPLEMENTED | Limits of agreement and mean difference. |
| ICC(2,1) | IMPLEMENTED | Shrout & Fleiss (1979) two-way random single measures. |
| Passing-Bablok Regression | IMPLEMENTED | Non-parametric slope and intercept with 95% CI. |
| Matthews Correlation Coeff (MCC) | IMPLEMENTED | Real contingency-based correlation. |
| Bayesian Credible Interval | IMPLEMENTED | Conjugate normal-normal posterior updating. |
| Meta-Analysis Engine | IMPLEMENTED | DerSimonian-Laird random effects meta-analysis. |
| Publication Exporter | IMPLEMENTED | Exports JSON archives, Markdown reports, and CSVs to disk. |

## Corpus & Data Providers (`vireon-corpus`)
| Dataset Provider | Status | Details |
|---|---|---|
| SyntheticSignalProvider | IMPLEMENTED | Deterministic synthetic EEG generation using `DeterministicRNG`. |
| PhysioNetMotorImageryProvider | IMPLEMENTED | Motor imagery EEG provider with checksum verification. |
| CHBMITProvider | IMPLEMENTED | CHB-MIT pediatric seizure EEG provider. |
| SleepEDFProvider | IMPLEMENTED | Sleep-EDF telemetry provider. |
| BIDS Standard Validator | IMPLEMENTED | BIDS directory structure validation. |

## Knowledge & Evidence Graph (`vireon-evidence`, `vireon-knowledge`)
| Component | Status | Details |
|---|---|---|
| Evidence Graph | IMPLEMENTED | In-memory NetworkX directed evidence graph with transaction logging. |
| Graph Query Engine | IMPLEMENTED | Multi-metric and dataset traversal. |
| Continuous Meta-Analysis | IMPLEMENTED | Graph-level random effects recomputation. |
| Decision Engine | IMPLEMENTED | Executable rule evaluation with full decision traces. |

## Deferred / Out of Scope for v0.2.0
| Component | Status | Note |
|---|---|---|
| Web GUI / Frontend | DEFERRED | Frontend deleted in T58; CLI and Python API serve as primary interfaces. |
| FastAPI Server | DEFERRED | Scope focused on library core and reproducible validation. |
