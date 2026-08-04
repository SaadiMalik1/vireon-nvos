# FDA Good Machine Learning Practice (GMLP) Compliance Mapping for VIREON

## Executive Overview
The US Food and Drug Administration (FDA), Health Canada, and the UK Medicines and Healthcare products Regulatory Agency (MHRA) jointly identified **10 Good Machine Learning Practice (GMLP)** principles for Medical Device Development. 

This document details how **VIREON (Neurotechnology Validation OS)** natively satisfies and enforces all 10 GMLP principles across software development, data management, model training, and continuous validation.

---

## The 10 FDA GMLP Principles & VIREON Traceability

### Principle 1: Multi-Disciplinary Expertise Is Leveraged Throughout the Total Product Lifecycle
- **FDA Requirement**: Deep understanding of clinical intended use, signal physics, and machine learning architecture throughout product development.
- **VIREON Compliance**:
  - Unites clinical signal processing contracts (`vireon-methods`), statistical verification (`vireon-validation`), and evidence management (`vireon-evidence`).
  - Standardizes validation metrics using clinical standards (ICC for multi-session stability, CCC for reference concordance, sensitivity/specificity for diagnostic claims).

---

### Principle 2: Good Software Engineering and Security Practices Are Implemented
- **FDA Requirement**: Software lifecycle management under IEC 62304 standards, unit testing, continuous integration, and secure code architecture.
- **VIREON Compliance**:
  - Modular package boundary architecture (`vireon-core`, `vireon-methods`, `vireon-validation`, `vireon-evidence`).
  - Enforces 100% CI automated test coverage across 360+ pytest suites on every git pull request.
  - Zero external unverified network calls during algorithm evaluation; fully deterministic execution via `DeterministicRNG`.

---

### Principle 3: Clinical Study Participants and Data Sets Are Representative of the Intended Patient Population
- **FDA Requirement**: Training and validation data must represent demographic, clinical, and physiological variability.
- **VIREON Compliance**:
  - Natively integrates multi-dataset providers across 4 open clinical EEG benchmark datasets: PhysioNet BCI, Sleep-EDF, CHB-MIT, and ERP CORE.
  - Implements Leave-One-Subject-Out (LOSO) cross-subject generalization benchmarks (`examples/scenario_cross_subject.py`) evaluating inter-subject variability across diverse demographics.

---

### Principle 4: Training and Test Data Sets Are Managed Independently
- **FDA Requirement**: Strict independence between training datasets and validation/test datasets to prevent data leakage and over-optimistic performance estimates.
- **VIREON Compliance**:
  - Enforces explicit seed locking and dataset splitting within `BenchmarkMatrix`.
  - Guarantees zero overlap between spatial filter fitting matrices and evaluation test epochs.

---

### Principle 5: Selected Reference Datasets Are Based on Best Available Methods
- **FDA Requirement**: Validation relies on robust reference standard datasets and gold-standard algorithm benchmarks.
- **VIREON Compliance**:
  - Compares all custom algorithms directly against validated gold-standard reference implementations (MNE-Python, SciPy, scikit-learn, mne-connectivity).
  - Requires Lin's Concordance Correlation Coefficient ($CCC \ge 0.95$) against established reference implementations prior to production deployment.

---

### Principle 6: Model Design Is Tailored to the Available Data and Reflects Intended Use
- **FDA Requirement**: Model architecture choices match physiological signal constraints and target clinical application.
- **VIREON Compliance**:
  - Implements physics-informed signal algorithms (FFT overlap-add fast convolution, Morlet wavelets, CSP spatial filtering, LCMV/MinimumNorm source localization).
  - Explicitly documents physical units ($\mu\text{V}$, $\text{Hz}$, $\mu\text{V}^2/\text{Hz}$) and scientific source literature citations (DOIs) for all methods.

---

### Principle 7: Focus Is Placed on the Performance of the Human-AI Team
- **FDA Requirement**: Evaluation of model interpretability, clinical actionable outputs, and human operator performance.
- **VIREON Compliance**:
  - Generates human-readable LaTeX reports, Jupyter notebooks, and HTML dashboards alongside machine-readable JSON-LD evidence bundles.
  - Integrates clear uncertainty metrics (bootstrap confidence intervals) to inform clinical decision-making.

---

### Principle 8: Testing Demonstrates Device Performance During Intended Conditions of Use
- **FDA Requirement**: Demonstration of robustness under real-world noise, signal perturbations, and hardware variation.
- **VIREON Compliance**:
  - Provides a built-in Perturbation Library (line noise, electrode pop, EMG muscle artifact, white noise).
  - Includes adversarial stress testing (`examples/scenario_adversarial_robustness.py`) using Fast Gradient Sign Method (FGSM) perturbations.

---

### Principle 9: Users Are Provided Clear, Essential Information
- **FDA Requirement**: Clear documentation of device performance, operating constraints, and algorithm limitations.
- **VIREON Compliance**:
  - Every execution produces a cryptographically signed `EvidenceBundle` containing exact execution parameters, dataset hashes, and statistical agreement metrics.
  - Interactive tutorials (`docs/tutorials/`) provide step-by-step guidance on reproducing all scientific claims.

---

### Principle 10: Deployed Models Are Monitored for Performance and Re-Training Needs Are Managed
- **FDA Requirement**: Post-market surveillance, continuous performance monitoring, and controlled algorithm updates.
- **VIREON Compliance**:
  - Stores all historical evidence runs in a persistent SQLite `EvidenceGraph`.
  - Enables queryable performance tracking (`ScientificLeaderboard`) to detect performance degradation over time or across software version releases.
