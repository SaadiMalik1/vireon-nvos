# VIREON API Reference — Validation Platform GA

Comprehensive API reference documentation for the VIREON Open Neurotechnology Platform.

---

## 1. vireon_core (Core Architecture & Contracts)

### `vireon_core.contracts.evidence.EvidenceBundle`
Immutable Pydantic model encapsulating execution provenance, statistical metrics, and verification hashes.

```python
class EvidenceBundle(BaseModel):
    evidence_hash: str
    algorithm: str
    dataset: str
    statistical_agreement: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=datetime.utcnow)
    environment: Dict[str, str] = Field(default_factory=dict)
    pass_fail: str = "PASS"
```

### `vireon_core.runtime.rng.DeterministicRNG`
Seeded, reproducible pseudorandom number generator wrapper for numerical stability.

```python
class DeterministicRNG:
    def __init__(self, seed: int = 42): ...
    def normal(self, loc=0.0, scale=1.0, size=None) -> np.ndarray: ...
    def uniform(self, low=0.0, high=1.0, size=None) -> np.ndarray: ...
    def integers(self, low: int, high: int, size=None) -> np.ndarray: ...
```

---

## 2. vireon_methods (Native Algorithms)

### Spectral Processing (`vireon_methods.spectral`)

#### `VireonFFT`
Fast Fourier Transform for 1D signals with periodogram scaling and windowing.
- **Reference:** `scipy.fft`, `scipy.signal.periodogram`
- **Signature:** `compute(signal: np.ndarray) -> Tuple[np.ndarray, np.ndarray]`

#### `VireonWelch`
Welch averaged periodogram spectral density estimation.
- **Reference:** Welch (1967), `scipy.signal.welch`
- **Signature:** `compute(signal: np.ndarray) -> Tuple[np.ndarray, np.ndarray]`

#### `VireonSTFT`
Short-Time Fourier Transform preserving time-frequency phase information.
- **Reference:** `scipy.signal.stft`
- **Signature:** `compute(signal: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]`

#### `VireonWavelet`
Continuous Morlet Wavelet Transform for multi-resolution time-frequency decomposition.
- **Reference:** MNE `tfr_array_morlet`, `scipy.signal.morlet2`
- **Signature:** `compute(signal: np.ndarray) -> np.ndarray`

#### `VireonMultitaper`
Multitaper PSD estimation using Slepian (DPSS) sequences.
- **Reference:** Thomson (1982), `scipy.signal.windows.dpss`
- **Signature:** `compute(signal: np.ndarray) -> Tuple[np.ndarray, np.ndarray]`

### Filtering (`vireon_methods.filtering`)

#### `VireonFIR`
Finite Impulse Response digital filter design and application using Hamming/Hann windows.
- **Reference:** `scipy.signal.firwin`, `scipy.signal.lfilter`
- **Signature:** `filter(signal: np.ndarray) -> np.ndarray`

#### `VireonIIR`
Infinite Impulse Response Butterworth filter with SOS (Second-Order Sections) zero-phase filtering.
- **Reference:** `scipy.signal.butter`, `scipy.signal.sosfiltfilt`
- **Signature:** `filter(signal: np.ndarray) -> np.ndarray`

### Spatial & Machine Learning (`vireon_methods.spatial`, `vireon_methods.machine_learning`)

#### `VireonICA`
Fast Independent Component Analysis for artifact decomposition.
- **Reference:** Hyvärinen & Oja (2000), `sklearn.decomposition.FastICA`
- **Signature:** `fit_transform(X: np.ndarray) -> np.ndarray`

#### `VireonCSP` / `CSPPlugin`
Common Spatial Patterns spatial filtering for 2-class motor imagery BCI.
- **Reference:** Ramoser et al. (2000), `mne.decoding.CSP`
- **Signature:** `fit_transform(X: np.ndarray, y: np.ndarray) -> np.ndarray`

### Source Localization (`vireon_methods.source_localization`)

#### `VireonLCMV`
Linearly Constrained Minimum Variance beamformer.
- **Reference:** Van Veen & Buckley (1988), `scipy.linalg.pinv`
- **Signature:** `fit(X: np.ndarray)` / `apply(X: np.ndarray) -> np.ndarray`

#### `VireonMinimumNorm`
Minimum Norm Estimate (MNE) inverse source localization.
- **Reference:** Hämäläinen & Ilmoniemi (1994), `scipy.linalg.solve`
- **Signature:** `fit(X: np.ndarray) -> np.ndarray`

### Connectivity (`vireon_methods.connectivity`)

#### `VireonCoherence` / `VireonPLV` / `VireonPLI` / `VireonWPLI` / `VireonAEC` / `VireonImaginaryCoherence`
Functional connectivity metrics quantifying spectral coherence, phase locking, and volume conduction-invariant phase synchrony.
- **Reference:** Vinck et al. (2011), `scipy.signal.coherence`
- **Signature:** `compute(X: np.ndarray, fs: float, band: Tuple[float, float]) -> np.ndarray`

### Time-Frequency & Signal Processing (`vireon_methods.time_frequency`, `vireon_methods.signal_processing`)

#### `VireonEMD`
Empirical Mode Decomposition for non-linear, non-stationary signals.
- **Reference:** Huang et al. (1998)
- **Signature:** `fit_transform(signal: np.ndarray) -> List[np.ndarray]`

#### `VireonConvolution`
1D linear convolution and cross-correlation.
- **Reference:** `np.convolve`, `np.correlate`
- **Signature:** `convolve(in1, in2)` / `correlate(in1, in2)`

---

## 3. vireon_validation (Validation Framework)

### `vireon_validation.statistics.framework.lin_concordance_correlation`
Computes Lin's Concordance Correlation Coefficient (CCC).

```python
def lin_concordance_correlation(x: np.ndarray, y: np.ndarray) -> float:
    """Computes Lin's CCC measuring agreement along the 45-degree line."""
    ...
```

### `vireon_validation.statistics.bootstrap.bootstrap_ccc_ci`
Computes 95% bootstrap confidence interval for Lin's CCC.

```python
def bootstrap_ccc_ci(x: np.ndarray, y: np.ndarray, n_bootstrap: int = 1000, confidence: float = 0.95, seed: int = 42) -> Dict[str, Any]:
    """Computes bootstrap confidence interval for Lin's CCC."""
    ...
```

### `vireon_validation.benchmarks.matrix.BenchmarkMatrix`
Matrix benchmarking coordinator across algorithms and datasets.

```python
class BenchmarkMatrix:
    def __init__(self, seed: int = 42): ...
    def add_method(self, method: Any): ...
    def add_dataset(self, name: str, data: np.ndarray, labels: Optional[np.ndarray] = None): ...
    def execute_matrix() -> List[Dict[str, Any]]: ...
```

---

## 4. vireon_evidence (Evidence Graph, Registry & Exporters)

### `vireon_evidence.registry.core.EvidenceRegistry`
SQLite-backed evidence bundle registry.

```python
class EvidenceRegistry:
    def __init__(self, db_path: str = "evidence_registry.db"): ...
    def register(self, bundle: EvidenceBundle): ...
    def retrieve(self, evidence_hash: str) -> Optional[EvidenceBundle]: ...
    def list_bundles(self) -> List[Dict[str, Any]]: ...
```

### `vireon_evidence.doi.EvidenceIdentifier`
Generates DataCite-compliant DOI metadata and identifiers.

```python
class EvidenceIdentifier:
    def __init__(self, prefix: str = "10.5072/vireon"): ...
    def mint(self, bundle: EvidenceBundle) -> str: ...
    def mint_with_metadata(self, bundle: EvidenceBundle) -> Dict[str, Any]: ...
```

### `vireon_evidence.exporters.jsonld_exporter.JSONLDExporter`
Exports evidence bundles to JSON-LD (Schema.org / W3C PROV-O).

```python
class JSONLDExporter:
    def export(self, bundle: EvidenceBundle) -> str: ...
```

---

## 5. vireon_api (REST API Endpoints)

- **GET `/api/health`**: Returns system health status and version.
- **GET `/api/evidence`**: Returns list of all persisted evidence bundles in SQLite registry.
- **GET `/api/evidence/{evidence_hash}`**: Retrieves detailed evidence bundle by hash.
- **POST `/api/benchmark`**: Executes BenchmarkMatrix and registers evidence bundle to SQLite store.
- **GET `/api/algorithms`**: Lists available algorithms and SRL readiness levels.

---

## 6. Scientific Reproducibility CLI

```bash
# Generate algorithm validation report
python scripts/generate_algorithm_validation_report.py

# Verify documentation sync
python scripts/check_doc_sync.py

# Verify tutorial execution
python scripts/verify_tutorial.py docs/tutorials/01_quickstart.md
```
