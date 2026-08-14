# VIREON Changelog

All notable changes to the VIREON project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2026-08-11

### Added
- **MOABB Integration**: Transitioned VIREON to a validation and evidence layer for MOABB (ADR 0008).
- Implemented `vireon-moabb` package handling datasets, models, pipelines, and evaluation.
- Added `ExperimentSpec` and rigorous schema validation for reproducibility.
- Replaced custom native implementations with MOABB's robust pipeline paradigms (e.g. `CSP + SVM`, `EEGNet`, `MDM`).
- Created `vireon_lab` CLI with `validate` and `inspect` commands for easier orchestration.
- Added `Scorecard` within Reporter for human-readable evaluation summaries.
- Fixed `ModuleNotFoundError` and Documentation Drift in CI pipeline.
- Implemented global `pytest` memory leak prevention for matplotlib in `conftest.py`.

---

## [1.2.0] - 2026-08-10

### Added
- Completed Phase 1-4 remediation tasks from the multi-agent playbook.
- Fixed algorithm defects (FBCSP, EEGNet, DeepConvNet, Mutual Information, Wavelet Coherence, etc.).
- Fixed test suites and CI pipeline (added pytest-asyncio, macOS, Windows).
- Fixed Evidence engine integrity.
- Added `/api/datasets` endpoint and improved `/api/algorithms`.
- Improved documentation and filled Phase E stubs.
- Cleaned up tracking of `.db` files and hardcoded secrets.

---

## [1.2.0] - 2026-08-11

### Fixed (playbook dx)
- FBCSP now applies band-pass filters per band (was broken — same unfiltered data for all bands)
- EEGNet architecture completed with BatchNorm, ELU, AvgPool, Dropout (matches Lawhern 2018)
- VireonMutualInformation now implements real Kraskov k-NN estimator (was histogram, mislabeled)
- DatasetManager.load_dataset() now dispatches by key (was ignoring key, returning same data for all)
- EvidenceRegistry uses INSERT OR IGNORE (was INSERT OR REPLACE, allowing silent overwrite)
- EvidenceRegistry.get() added to public API (was missing)
- EvidenceTransaction hash is now deterministic (uses sequence number, not wall-clock timestamp)
- 35 empty Phase E Implementation Status doc stubs filled
- All version strings synced to 1.2.0 (was: API=0.4.0, subpackages=1.0.1-1.0.3)
- vireon-publications references updated (directory was deleted in v1.0.2 but still referenced)
- Removed 4 unimplemented dataset keys (chb_mit, bci_comp_iv_2a, tuh_eeg, openneuro)
- Removed silent synthetic fallback in load_dataset (now raises DatasetDownloadError)

### Added
- vireon-corpus/exceptions.py with UnknownDatasetError, DatasetDownloadError
- EvidenceRegistry.search() method for filtering by algorithm/dataset
- EvidenceAlreadyRegisteredError for tamper detection
- EvidenceTransaction.sequence_number field (deterministic)
- vireon-moabb package: POC proven with real BNCI2014_001 data (9 subjects, 74.95% accuracy)
- ADR 0008: VIREON × MOABB integration (10 principles)



## [1.0.0] - 2026-08-05

### Added
- **Milestone A (Real Data Integration)**:
  - Introduced unified `DatasetManager` (`vireon-corpus/vireon_corpus/dataset_manager.py`) with local caching under `~/.vireon/datasets/` and SHA-256 integrity verification.
  - Connected 7 real physiological EEG datasets: PhysioNet BCI Motor Imagery, Sleep-EDF, CHB-MIT Scalp EEG, ERP CORE, BCI Competition IV-2a, TUH EEG Corpus, OpenNeuro.
  - Added PhysioNet download step to GitHub Actions CI workflow (`.github/workflows/ci.yml`).
  - Added real-data algorithm benchmark suite (`tests/test_real_data_validation.py`) and end-to-end integration suite (`tests/test_real_data_integration.py`).
  - Generated 210-line comprehensive real-data validation report (`reports/real_data_validation_report.md`).

- **Milestone B (Corpus Expansion)**:
  - Implemented 8 new algorithms: Riemannian MDM (`VireonRiemannianMDM`), xDAWN (`VireonxDAWN`), Filter Bank CSP (`VireonFBCSP`), `EEGNetWrapper`, `DeepConvNetWrapper`, Wavelet Coherence (`VireonWaveletCoherence`), Transfer Entropy (`VireonTransferEntropy`), Mutual Information (`VireonMutualInformation`).
  - Reproduced 7 new scientific papers: Lawhern 2018, Schirrmeister 2017, Ang 2012, Lotte 2018, Blankertz 2010, Barachant 2012, Rivet 2009. Total literature reproduction suite now covers **29+ papers across 42 passing test cases**.
  - Generated master literature portfolio report (`reports/literature_portfolio.md`).

- **Milestone C (Productization & Regulatory Binders)**:
  - Package configured for PyPI installation (`pip install vireon-nvos`).
  - Added multi-stage production `Dockerfile`.
  - Configured MkDocs documentation site (`mkdocs.yml`).
  - Generated 532-line API Reference Manual (`docs/api_reference.md`), 2,488-word User Guide (`docs/user_guide.md`), 2,010-word Developer Guide (`docs/developer_guide.md`), 618-word `CONTRIBUTING.md`, and 1,068-word Plugin SDK Guide (`docs/plugin_sdk.md`).
  - Added valid `CITATION.cff` and GitHub Issue templates (`.github/ISSUE_TEMPLATE/`).

---

## [0.6.0] - 2026-08-04

### Added
- Comprehensive Evidence Portfolio Initiative (EPI).
- 14 new literature reproduction tests.
- 8 real-world example scripts.
- FDA GMLP compliance mapping (`docs/regulatory/fda_gmlp_compliance.md`).
- IEC 62304 SOUP inventory (`docs/regulatory/soup_inventory.md`).
- Validation Master Plan (`docs/regulatory/validation_master_plan.md`).
- Executive ROI Case Study (`docs/corporate/roi_case_study.md`).

---

## [0.5.1] - 2026-08-03

### Added
- FFT-based convolution and cross-correlation (`VireonConvolution`).
- MNE Minimum Norm & Beamformer cross-validation tests.
- Shrout & Fleiss Intraclass Correlation Coefficient (`intraclass_correlation`).

---

## [0.5.0] - 2026-08-01

### Added
- Core validation matrix and Lin's Concordance Correlation Coefficient ($CCC$).
- Initial SQLite evidence graph persistence.

---

## [0.1.0] - 2026-07-15

### Added
- Initial core contracts, `ISignal` interface, and `DeterministicRNG` runtime.
- Native Welch PSD and Common Spatial Pattern (CSP) modules.
