# Validation Master Plan (VMP) — VIREON Neurotechnology Validation Platform

**Document Identifier:** VMP-VIREON-2026-V1  
**Compliance Standards:** ISO 14971:2019 (Risk Management), IEC 62304:2015 (Medical Device Software Life Cycle), FDA Guidance on Good Machine Learning Practice (GMLP)  
**Effective Release:** v0.6.0-evidence-portfolio  

---

## 1. Purpose & Scope

### 1.1 Purpose
This Validation Master Plan (VMP) defines the strategic framework, organizational roles, verification methodologies, risk controls, and regulatory evidence requirements for validating **VIREON (Neurotechnology Validation OS)** as a Software as a Medical Device (SaMD) validation framework and enterprise research platform.

The objective of this VMP is to provide undeniable documented evidence that VIREON consistently performs according to its intended scientific use, produces numerically exact and reproducible outputs, and complies with international medical device quality standards.

### 1.2 Scope
This plan governs all software components within the VIREON repository, including:
1. `vireon-core`: Core contract definitions, deterministic runtime, and evidence bundle schemas.
2. `vireon-methods`: Signal processing, time-frequency, spatial filtering, connectivity, and source localization algorithms.
3. `vireon-validation`: Statistical verification framework, Lin's Concordance Correlation Coefficient (CCC), Intraclass Correlation Coefficient (ICC), and perturbation matrix testing.
4. `vireon-evidence`: SQLite EvidenceGraph, query engines, and regulatory export engines.
5. `vireon-verification`: Literature reproduction suite (20+ verified paper reproductions).

---

## 2. Regulatory Compliance & Standards Matrix

| Standard / Regulation | Title | VIREON Implementation Mechanism |
|---|---|---|
| **IEC 62304:2015** | Medical device software — Software life cycle processes | Modular package architecture, automated unit/integration test suite, SOUP inventory management. |
| **ISO 14971:2019** | Medical devices — Application of risk management to medical devices | Perturbation matrix testing (line noise, muscle artifact, electrode pop, FGSM adversarial attack). |
| **FDA GMLP (2021)** | Good Machine Learning Practice for Medical Device Development | 10-principle alignment mapping, independent train/test splits, gold-standard reference cross-validation. |
| **21 CFR Part 11** | Electronic Records; Electronic Signatures | Cryptographic SHA-256 evidence hashing, immutable SQLite graph ledger, reproducible execution tracing. |

---

## 3. System Description & Architectural Boundaries

VIREON is an open-source, deterministic neurotechnology validation platform designed to eliminate false claims, unrepeatable metrics, and unverified software dependencies in physiological signal processing.

```
+-----------------------------------------------------------------------------------+
|                            VIREON ARCHITECTURE BOUNDARY                           |
|                                                                                   |
|  +-------------------------+      +-------------------------+                     |
|  |     vireon-methods      |      |    vireon-validation    |                     |
|  |  Signal Processing &    | ---->| Statistical Verification|                     |
|  |  Spatial Filtering      |      |  (CCC >= 0.95 / ICC)    |                     |
|  +-------------------------+      +-------------------------+                     |
|               |                                |                                  |
|               v                                v                                  |
|  +----------------------------------------------------------+                     |
|  |                     vireon-evidence                      |                     |
|  |          SQLite EvidenceGraph & SHA-256 Bundles          |                     |
|  +----------------------------------------------------------+                     |
|                               |                                                   |
|                               v                                                   |
|  +----------------------------------------------------------+                     |
|  |                 Regulatory Export Engine                 |                     |
|  |      (FDA GMLP Binders, SOUP, VMP Audit Deliverables)    |                     |
|  +----------------------------------------------------------+                     |
+-----------------------------------------------------------------------------------+
```

---

## 4. Risk Management Integration (ISO 14971)

Risk management is embedded directly into VIREON's automated validation pipeline. Signal processing risks are identified, evaluated, and controlled through systematic perturbation testing.

### 4.1 Hazard Identification & Risk Controls

| Risk ID | Failure Mode / Hazard | Potential Clinical / Scientific Impact | Automated Risk Control in VIREON | Residual Risk Level |
|---|---|---|---|---|
| **R-01** | Numerical instability in matrix inversion during beamforming (LCMV/MinimumNorm). | Division by zero or NaN source power output, mislocalizing epileptic focus. | Tikhonov regularization scaling (`lambda2` SNR normalization) + condition number check. | **Negligible** |
| **R-02** | Eigenvector sign ambiguity in spatial filtering (CSP/ICA). | Phase inversion causing erroneous negative concordance scores. | Component-aligned variance sorting and polarity-invariant feature matching. | **Negligible** |
| **R-03** | Volume conduction artifacts distorting spectral connectivity estimates. | Spurious phase synchronization between distant scalp channels. | Implementation of volume-conduction-robust metrics (`VireonWPLI`, `VireonAEC`). | **Negligible** |
| **R-04** | Adversarial or out-of-distribution noise corrupting classifier outputs. | Unpredicted degradation of BCI classification accuracy in live patient use. | Systematic perturbation matrix stress testing (`WhiteNoise`, `LineNoise`, FGSM attacks). | **Acceptable** |
| **R-05** | Non-deterministic random seed initialization across execution environments. | Unrepeatable validation metrics between local dev and CI pipelines. | Centralized `DeterministicRNG` seed locking across all random sampling routines. | **Negligible** |

---

## 5. Verification & Validation Strategy (IEC 62304)

### 5.1 Verification Protocol (Software Testing)
VIREON employs a 3-tier testing methodology executed automatically via Pytest and GitHub Actions CI:

1. **Unit Testing (Tier 1)**:
   - Verifies individual function behavior, boundary conditions, and mathematical contracts.
   - Requires 100% pass rate across 360+ tests.
2. **Numerical Cross-Validation (Tier 2)**:
   - Evaluates every custom algorithm against established reference standards (MNE-Python, SciPy, scikit-learn, mne-connectivity).
   - Enforces strict quantitative thresholds: Lin's Concordance Correlation Coefficient ($CCC \ge 0.95$) or Intraclass Correlation Coefficient ($ICC \ge 0.85$).
3. **Literature Reproduction Suite (Tier 3)**:
   - Reproduces 20+ landmark published papers spanning 5 subfields (BCI, Clinical, Sleep, Epilepsy, Cognitive) and 2 eras (1967-2012 classic, 2020-2022 recent).

### 5.2 Acceptance Criteria
A software build is deemed validated if and only if:
- All 360+ pytest tests pass with 0 failures (`pytest --tb=no -q`).
- All 20+ literature reproduction tests pass (`pytest vireon-verification/literature/ -v`).
- Zero hardcoded point estimates or fake metrics exist in verification files.
- Cryptographic SHA-256 evidence bundles are generated for all validation executions.

---

## 6. SOUP Management Strategy

Software of Unknown Provenance (SOUP) dependencies are managed under strict IEC 62304 processes:
- All direct dependencies (NumPy, SciPy, scikit-learn, MNE-Python, PyYAML) are documented in the SOUP Inventory (`docs/regulatory/soup_inventory.md`).
- Automated dependency scanning and version locking ensure no unvetted upstream updates enter the build pipeline.
- Critical numerical algorithms inside SOUP libraries (e.g., SciPy FFT) are continuously cross-validated by VIREON's test suite.

---

## 7. Change Control & Re-Validation Protocol

Any modification to VIREON source code, mathematical algorithms, or configuration files triggers automated re-validation:
1. **Branch Protection**: Direct commits to `main` are restricted. All changes require feature branches (`epi/E<NN>-<slug>`) and Pull Requests.
2. **Automated CI Regression**: GitHub Actions automatically runs the entire test suite on every PR push.
3. **Evidence Hashing**: Any change altering numerical output changes the resulting `EvidenceBundle` SHA-256 hash, ensuring full traceability of version drift.

---

## 8. Detailed Verification & Traceability Protocol Matrix

This section establishes the detailed traceability matrix mapping system requirements, scientific algorithms, regulatory hazards, and automated test cases across the VIREON suite:

| Requirement ID | Module / Function | Regulatory Hazard (ISO 14971) | Verification Test Case | Acceptance Criteria |
|---|---|---|---|---|
| **REQ-DSP-001** | `VireonWelch` | Spectral power density distortion under non-stationary signals. | `test_welch_recovers_known_psd` | Peak frequency within $\pm 0.2\text{ Hz}$, variance reduction verified. |
| **REQ-DSP-002** | `VireonMultitaper` | High spectral leakage in narrow-band oscillatory signals. | `test_algorithm_comparison` | Lin's $CCC \ge 0.85$ vs Welch reference estimate. |
| **REQ-DSP-003** | `VireonSTFT` | Boundary truncation artifacts in short-time windowing. | `test_truong_2020` | Spectrogram magnitude $> 0.5$ under pre-ictal gamma surge. |
| **REQ-DSP-004** | `VireonWavelet` | Morlet wavelet phase distortion under complex frequency grids. | `test_zhang_2021` | Wavelet energy ratio $> 2.0$ for target 3 Hz spike frequency. |
| **REQ-SPT-001** | `VireonCSP` | Matrix singular value breakdown in high-density EEG. | `test_blankertz_2008` | Binary classification accuracy $> 0.85$ under LDA. |
| **REQ-SPT-002** | `VireonICA` | Non-convergence of FastICA fixed-point iteration. | `test_makeig_1996` | Component matrix shape exact, 0 NaN values generated. |
| **REQ-SRC-001** | `VireonLCMV` | Dipole location distortion under noisy covariance estimates. | `test_lcmv_matches_mne` | Lin's $CCC \ge 0.95$ vs MNE-Python `mne.beamformer`. |
| **REQ-SRC-002** | `VireonMinimumNorm` | Unregulated $L_2$ norm regularization distortion. | `test_mne_uses_lambda2` | Distinct source estimate outputs under varying SNR $\lambda^2$. |
| **REQ-CON-001** | `VireonWPLI` | Spurious phase locking induced by volume conduction. | `test_vinck_2011` | $WPLI \approx 0.0$ under zero phase lag volume conduction. |
| **REQ-CON-002** | `VireonAEC` | Amplitude envelope correlation distortion due to field spread. | `test_hipp_2012` | $AEC$ correlation matrix generated without NaNs. |

---

## 9. Data Integrity, Traceability & Cryptographic Hashing Protocol

Data integrity and traceability under 21 CFR Part 11 and FDA GMLP are governed by VIREON's cryptographic evidence pipeline:

### 9.1 EvidenceBundle Schema & Immutability
Every algorithm evaluation run automatically produces an immutable `EvidenceBundle` JSON object containing:
1. `evidence_hash`: A deterministic 64-character SHA-256 hash calculated over the algorithm name, dataset identity, numerical metrics, and system configuration.
2. `algorithm`: The qualified string identifier of the algorithm evaluated.
3. `dataset`: The verified name or accession number of the clinical/research dataset.
4. `statistical_agreement`: Quantitative agreement metrics (CCC, ICC, Accuracy, Sensitivity, Specificity, Latency).

### 9.2 EvidenceGraph SQLite Persistence & Querying
Evidence bundles are committed to a local or enterprise SQLite database (`EvidenceGraph`). The graph maintains foreign-key relationships between `EvidenceBundleNode`, `MethodNode`, and `DatasetNode`. Audit panels and QA managers can query historical execution trends via the `ScientificLeaderboard` and `ContinuousMetaAnalysis` APIs to verify performance stability across software releases.

---

## 10. Audit Preparedness & Inspection Strategy

To ensure seamless inspection readiness for FDA, EU Notified Body, or ISO auditors, the following inspection binder procedure is enforced:

### 10.1 Inspection Package Generation
Prior to audit submission or on-site inspection, executing `python examples/example_regulatory_submission.py` generates the complete digital audit binder containing:
- Signed Validation Master Plan (`docs/regulatory/validation_master_plan.md`)
- FDA GMLP Compliance Mapping (`docs/regulatory/fda_gmlp_compliance.md`)
- Complete SOUP Inventory (`docs/regulatory/soup_inventory.md`)
- Corporate ROI Case Study (`docs/corporate/roi_case_study.md`)
- Executive Evidence Portfolio (`EVIDENCE_PORTFOLIO.md`)
- Complete Pytest Execution Log showing 100% test pass rate across 360+ tests.

### 10.2 Continuous Inspection Readiness
Because VIREON embeds verification tests directly into CI/CD build pipelines, the software system remains in a constant state of inspection readiness. Any code commit violating numerical contracts, hardcoding test metrics, or failing reference cross-validations is automatically blocked prior to merge.

---

## 11. Documentation & Deliverables Summary

Upon completion of validation activities under this VMP, the following formal audit binder is produced:
1. **Validation Master Plan (VMP)** (`docs/regulatory/validation_master_plan.md`)
2. **FDA GMLP Compliance Mapping** (`docs/regulatory/fda_gmlp_compliance.md`)
3. **SOUP Dependency Inventory** (`docs/regulatory/soup_inventory.md`)
4. **Corporate ROI Case Study** (`docs/corporate/roi_case_study.md`)
5. **Evidence Portfolio Executive Summary** (`EVIDENCE_PORTFOLIO.md`)
6. **Public Reproducibility Guide** (`docs/reproducibility_guide.md`)

---

## 13. Appendix A: Quantitative Conformance Testing & Tolerance Standards

To ensure zero ambiguity during internal QA reviews and external regulatory audits, VIREON defines strict mathematical acceptance criteria across all 6 core scientific categories:

### 13.1 Power Spectral Density (PSD) Conformance Standards
- **Reference Standard**: SciPy Signal Processing (`scipy.signal.welch`) & MNE-Python (`mne.time_frequency.psd_array_welch`).
- **Concordance Metric**: Lin's Concordance Correlation Coefficient ($CCC \ge 0.95$).
- **Frequency Grid Precision**: Maximum acceptable peak frequency drift $\le \pm 0.1\text{ Hz}$.

### 13.2 Time-Frequency Representation (TFR) Conformance Standards
- **Reference Standard**: MNE-Python Morlet Wavelet TFR (`mne.time_frequency.tfr_array_morlet`).
- **Concordance Metric**: Spectral energy ratio $CCC \ge 0.95$ across 0.5–100 Hz frequency range.
- **Phase Preservation**: Complex phase angle deviation $\le 0.05\text{ rad}$.

### 13.3 Spatial Filtering (CSP & ICA) Conformance Standards
- **Reference Standard**: MNE-Python CSP (`mne.decoding.CSP`) & scikit-learn FastICA (`sklearn.decomposition.FastICA`).
- **Concordance Metric**: Component-aligned variance ratio $CCC \ge 0.80$.
- **Classification Performance**: Linear Discriminant Analysis (LDA) cross-validation accuracy $\ge 0.85$ on benchmark motor imagery.

### 13.4 Functional Connectivity Conformance Standards
- **Reference Standard**: MNE-Connectivity (`mne_connectivity.spectral_connectivity_epochs`).
- **Concordance Metric**: $CCC \ge 0.95$ across all 6 implemented spectral connectivity metrics (Coherence, PLV, PLI, WPLI, ImCoh, AEC).
- **Volume Conduction Suppression**: Phase Lag Index ($PLI$) and Weighted Phase Lag Index ($WPLI$) must yield $0.00 \pm 0.01$ under zero-phase-lag simulated volume conduction.

### 13.5 Source Localization Conformance Standards
- **Reference Standard**: MNE Beamforming (`mne.beamformer.make_lcmv`) & Minimum Norm (`mne.minimum_norm.make_inverse_operator`).
- **Concordance Metric**: Source power spatial correlation $CCC \ge 0.90$.
- **Regularization Dynamics**: Inverse operator must demonstrate statistically distinct source estimates under changing SNR regularization ($\lambda^2$).

---

## 14. Appendix B: ISO 14971 Risk Assessment & Mitigation Protocols

### 14.1 Risk Evaluation Matrix & Severity Definitions
ISO 14971 requires a quantitative pre-mitigation and post-mitigation Risk Priority Number (RPN) calculation:

$$\text{RPN} = \text{Severity (S)} \times \text{Occurrence (O)} \times \text{Detection (D)}$$

Where:
- **Severity (S)**: Scale 1 (Minor software glitch) to 5 (Critical diagnostic misclassification).
- **Occurrence (O)**: Scale 1 (Remote event $< 0.1\%$) to 5 (Frequent event $> 10\%$).
- **Detection (D)**: Scale 1 (Always caught by CI build) to 5 (Undetectable in production).

### 14.2 Quantitative Risk Control Verification

1. **Hazard R-01 (LCMV Singular Value Matrix Breakdown)**:
   - *Pre-Mitigation*: $S = 4, O = 3, D = 4 \implies \mathbf{\text{RPN} = 48}$ (High Risk).
   - *Control*: `VireonLCMV` condition number thresholding and Tikhonov regularized noise covariance estimation.
   - *Post-Mitigation*: $S = 4, O = 1, D = 1 \implies \mathbf{\text{RPN} = 4}$ (Negligible Risk).

2. **Hazard R-02 (Spatial Filter Eigenvector Polarity Inversion)**:
   - *Pre-Mitigation*: $S = 3, O = 4, D = 4 \implies \mathbf{\text{RPN} = 48}$ (High Risk).
   - *Control*: Absolute log variance feature transformation and variance-sorted component alignment.
   - *Post-Mitigation*: $S = 3, O = 1, D = 1 \implies \mathbf{\text{RPN} = 3}$ (Negligible Risk).

3. **Hazard R-03 (Phase Synchronization Conduction Distortion)**:
   - *Pre-Mitigation*: $S = 4, O = 4, D = 3 \implies \mathbf{\text{RPN} = 48}$ (High Risk).
   - *Control*: Mandatory deployment of volume-conduction-insensitive phase metrics (`WPLI`, `AEC`).
   - *Post-Mitigation*: $S = 4, O = 1, D = 1 \implies \mathbf{\text{RPN} = 4}$ (Negligible Risk).

---

## 15. Approval & Sign-Off Matrix

| Role | Name / Title | Signature | Date |
|---|---|---|---|
| **Head of Quality Assurance** | QA Lead, VIREON Quality System | *Approved via Automated CI Gate* | 2026-08-04 |
| **Lead Systems Architect** | Principal Engineer, Neurotechnology OS | *Approved via Git Tag v0.6.0* | 2026-08-04 |
| **Regulatory Affairs Director** | Director of SaMD Compliance | *Approved via EvidenceGraph Ledger* | 2026-08-04 |
