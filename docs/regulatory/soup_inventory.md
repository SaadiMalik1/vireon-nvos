# Software of Unknown Provenance (SOUP) Inventory & Dependency Assessment

## 1. Regulatory Context
Under **IEC 62304 Section 5.3.3 / 5.3.4 (Medical Device Software — Software Life Cycle Processes)**, all third-party libraries, open-source packages, and external software components integrated into a Software as a Medical Device (SaMD) system must be inventoried, assessed for risk (ISO 14971), and assigned explicit anomaly tracking procedures.

This document serves as the formal **SOUP Inventory** for **VIREON (v1.0.1 Production Release)**.

---

## 2. Master SOUP Dependency Table

| Package Name | Version Specifier | Primary Function / Usage in VIREON | IEC 62304 Class | ISO 14971 Risk Level | Anomaly Tracking Source |
|---|---|---|---|---|---|
| **Python** | `>= 3.10` | Core Execution Runtime Environment | Class B | Low | [python.org/bugs](https://bugs.python.org) |
| **NumPy** | `>= 1.24.0` | N-dimensional array manipulation & linear algebra | Class B | Low | [github.com/numpy/numpy/issues](https://github.com/numpy/numpy/issues) |
| **SciPy** | `>= 1.10.0` | FFT, STFT, signal filtering, and optimization | Class B | Low | [github.com/scipy/scipy/issues](https://github.com/scipy/scipy/issues) |
| **scikit-learn** | `>= 1.2.0` | Linear Discriminant Analysis (LDA), ICA, metrics | Class B | Medium | [github.com/scikit-learn/scikit-learn/issues](https://github.com/scikit-learn/scikit-learn/issues) |
| **MNE-Python** | `>= 1.3.0` | Reference standard for EEG/MEG analysis & beamforming | Class A | Low | [github.com/mne-tools/mne-python/issues](https://github.com/mne-tools/mne-python/issues) |
| **mne-connectivity** | `>= 0.5.0` | Reference standard for spectral connectivity metrics | Class A | Low | [github.com/mne-tools/mne-connectivity/issues](https://github.com/mne-tools/mne-connectivity/issues) |
| **mne-bids** | `>= 0.12.0` | BIDS standard format parsing and validation | Class A | Low | [github.com/mne-tools/mne-bids/issues](https://github.com/mne-tools/mne-bids/issues) |
| **edfio** | `>= 0.4.0` | Pure-Python EDF file reader/writer | Class A | Low | [github.com/edfio/edfio/issues](https://github.com/edfio/edfio/issues) |
| **pydantic** | `>= 2.0.0` | Data validation and evidence schema enforcement | Class B | Low | [github.com/pydantic/pydantic/issues](https://github.com/pydantic/pydantic/issues) |
| **networkx** | `>= 3.0` | Causal graph and DAG execution routing | Class A | Low | [github.com/networkx/networkx/issues](https://github.com/networkx/networkx/issues) |
| **fastapi** | `>= 0.100.0` | REST API service container and endpoint router | Class A | Low | [github.com/tiangolo/fastapi/issues](https://github.com/tiangolo/fastapi/issues) |
| **httpx** | `>= 0.24.0` | Asynchronous HTTP client for remote evidence validation | Class A | Low | [github.com/encode/httpx/issues](https://github.com/encode/httpx/issues) |
| **statsmodels** | `>= 0.14.0` | Advanced statistical validation and regression models | Class A | Low | [github.com/statsmodels/statsmodels/issues](https://github.com/statsmodels/statsmodels/issues) |
| **hypothesis** | `>= 6.0.0` | Property-based test generation and invariant testing | Class A | Low | [github.com/HypothesisWorks/hypothesis/issues](https://github.com/HypothesisWorks/hypothesis/issues) |
| **pytest** | `>= 7.2.0` | Automated test runner and assertion framework | Class A | Low | [github.com/pytest-dev/pytest/issues](https://github.com/pytest-dev/pytest/issues) |
| **PyYAML** | `>= 6.0` | Configuration parsing and evidence serialization | Class A | Low | [github.com/yaml/pyyaml/issues](https://github.com/yaml/pyyaml/issues) |

---

## 3. SOUP Risk Controls and Mitigation Strategy

1. **Version Pinning & Lockfiles**:
   - All SOUP dependencies are strictly specified in `requirements.txt` and verified during continuous integration builds.
2. **Gold-Standard Cross-Validation**:
   - Every numerical output produced by third-party SOUP functions (e.g., SciPy FFT, MNE Beamformer) is cross-validated against independent reference algorithms via Lin's Concordance Correlation Coefficient ($CCC \ge 0.99$).
3. **Deterministic Isolation**:
   - Random number generation in third-party SOUP libraries is encapsulated by VIREON's `DeterministicRNG` to guarantee 100% reproducible execution.
