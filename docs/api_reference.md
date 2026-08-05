# VIREON Complete API Reference Manual (v1.0.0)

---

## Package Structure Overview
- `vireon_core`: Contracts, contracts for evidence, deterministic runtime, plugin contracts
- `vireon_methods`: Signal processing, spectral analysis, spatial filtering, connectivity, source localization, deep learning
- `vireon_validation`: Lin's CCC, ICC, perturbation matrix, benchmarking
- `vireon_evidence`: SQLite EvidenceGraph, registry, query engines, report exporters
- `vireon_corpus`: DatasetManager, data caching, checksum verification

---

## 1. `vireon_core` Package

### 1.1 `vireon_core.contracts.base`
```python
class ISignal:
    """Base interface for 1D, 2D, and 3D physiological signals."""
    data: np.ndarray
    sample_rate: float
    channel_names: List[str]
```

### 1.2 `vireon_core.contracts.evidence`
```python
class EvidenceBundle(BaseModel):
    """Cryptographic evidence bundle containing hash, metrics, and parameters."""
    bundle_id: str
    evidence_hash: str
    timestamp: str
    algorithm: str
    dataset: str
    statistical_agreement: Dict[str, Any]
    runtime_sec: float
```

### 1.3 `vireon_core.runtime.rng`
```python
class DeterministicRNG:
    """Centralized seed-locked random number generator."""
    def __init__(self, seed: int = 42): ...
    def normal(self, loc=0.0, scale=1.0, size=None) -> np.ndarray: ...
    def uniform(self, low=0.0, high=1.0, size=None) -> np.ndarray: ...
```

---

## 2. `vireon_methods` Package

### 2.1 `vireon_methods.spectral.vireon_welch`
```python
class VireonWelch:
    """Welch Power Spectral Density (PSD) estimator."""
    def __init__(self, fs: float = 250.0, nperseg: int = 256, noverlap: Optional[int] = None): ...
    def compute(self, signal: np.ndarray) -> Tuple[np.ndarray, np.ndarray]: ...
```

### 2.2 `vireon_methods.spectral.vireon_multitaper`
```python
class VireonMultitaper:
    """Thomson Multitaper PSD estimator with DPSS tapers."""
    def __init__(self, fs: float = 250.0, NW: float = 2.5, n_tapers: Optional[int] = None): ...
    def compute(self, signal: np.ndarray) -> Tuple[np.ndarray, np.ndarray]: ...
```

### 2.3 `vireon_methods.spectral.vireon_stft`
```python
class VireonSTFT:
    """Short-Time Fourier Transform spectrogram estimator."""
    def __init__(self, fs: float = 250.0, nperseg: int = 128, noverlap: Optional[int] = None): ...
    def compute(self, signal: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]: ...
```

### 2.4 `vireon_methods.spectral.vireon_wavelets`
```python
class VireonWavelet:
    """Continuous Wavelet Transform (Morlet, Paul, DOG, Mexican Hat)."""
    def __init__(self, fs: float, frequencies: np.ndarray, wavelet: str = "morlet"): ...
    def compute(self, signal: np.ndarray) -> np.ndarray: ...
```

### 2.5 `vireon_methods.spatial.vireon_csp`
```python
class VireonCSP:
    """Common Spatial Pattern spatial filter for 2-class motor imagery."""
    def __init__(self, n_components: int = 4): ...
    def fit(self, X: np.ndarray, y: np.ndarray): ...
    def transform(self, X: np.ndarray) -> np.ndarray: ...
    def fit_transform(self, X: np.ndarray, y: np.ndarray) -> np.ndarray: ...
```

### 2.6 `vireon_methods.spatial.vireon_ica`
```python
class VireonICA:
    """FastICA blind source separation for EEG artifacts."""
    def __init__(self, n_components: int = 4, max_iter: int = 200, tol: float = 1e-4): ...
    def fit(self, X: np.ndarray): ...
    def transform(self, X: np.ndarray) -> np.ndarray: ...
    def fit_transform(self, X: np.ndarray) -> np.ndarray: ...
```

### 2.7 `vireon_methods.spatial.vireon_riemannian`
```python
class VireonRiemannianMDM:
    """Riemannian Geometry Minimum Distance to Mean (MDM) classifier."""
    def __init__(self): ...
    def fit(self, X: np.ndarray, y: np.ndarray): ...
    def predict(self, X: np.ndarray) -> np.ndarray: ...
```

### 2.8 `vireon_methods.spatial.vireon_xdawn`
```python
class VireonxDAWN:
    """xDAWN spatial filter for ERP signal enhancement."""
    def __init__(self, n_filter: int = 2): ...
    def fit(self, X: np.ndarray, y: np.ndarray): ...
    def transform(self, X: np.ndarray) -> np.ndarray: ...
```

### 2.9 `vireon_methods.spatial.vireon_fbcsp`
```python
class VireonFBCSP:
    """Filter Bank Common Spatial Pattern (FBCSP)."""
    def __init__(self, n_components: int = 2, bands: Optional[List[Tuple[float, float]]] = None): ...
    def fit_transform(self, X: np.ndarray, y: np.ndarray) -> np.ndarray: ...
```

### 2.10 `vireon_methods.connectivity.vireon_connectivity`
```python
class VireonWPLI:
    """Weighted Phase Lag Index (WPLI) functional connectivity estimator."""
    def compute(self, data: np.ndarray, fs: float, band: Tuple[float, float]) -> float: ...

class VireonAEC:
    """Orthogonalized Amplitude Envelope Correlation (AEC) estimator."""
    def compute(self, data: np.ndarray, fs: float, band: Tuple[float, float]) -> np.ndarray: ...
```

### 2.11 `vireon_methods.connectivity.vireon_wavelet_coherence`
```python
class VireonWaveletCoherence:
    """Time-frequency wavelet cross-coherence estimator."""
    def compute(self, data: np.ndarray, fs: float = 250.0) -> np.ndarray: ...
```

### 2.12 `vireon_methods.connectivity.vireon_transfer_entropy`
```python
class VireonTransferEntropy:
    """Transfer entropy directional information flow estimator."""
    def compute(self, x: np.ndarray, y: np.ndarray, delay: int = 1) -> float: ...
```

### 2.13 `vireon_methods.connectivity.vireon_mutual_information`
```python
class VireonMutualInformation:
    """Mutual information non-linear connectivity estimator."""
    def compute(self, x: np.ndarray, y: np.ndarray) -> float: ...
```

### 2.14 `vireon_methods.deep_learning.eegnet`
```python
class EEGNetWrapper:
    """Compact Convolutional Neural Network wrapper."""
    def __init__(self, n_classes: int = 2, channels: int = 8, samples: int = 250): ...
    def fit(self, X: np.ndarray, y: np.ndarray): ...
    def predict(self, X: np.ndarray) -> np.ndarray: ...
```

### 2.15 `vireon_methods.deep_learning.deepconvnet`
```python
class DeepConvNetWrapper:
    """Deep Convolutional Neural Network wrapper."""
    def __init__(self, n_classes: int = 2, channels: int = 8, samples: int = 250): ...
    def fit(self, X: np.ndarray, y: np.ndarray): ...
    def predict(self, X: np.ndarray) -> np.ndarray: ...
```

### 2.16 `vireon_methods.source_localization.vireon_beamforming`
```python
class VireonLCMV:
    """Linearly Constrained Minimum Variance (LCMV) beamformer."""
    def __init__(self, leadfield: np.ndarray, reg: float = 0.05): ...
    def fit_transform(self, X: np.ndarray) -> np.ndarray: ...
```

### 2.17 `vireon_methods.source_localization.vireon_source_localization`
```python
class VireonMinimumNorm:
    """Minimum Norm Estimate (MNE / dSPM / sLORETA) source localization."""
    def __init__(self, leadfield: np.ndarray, lambda2: float = 0.1): ...
    def fit_transform(self, X: np.ndarray) -> np.ndarray: ...
```

---

## 3. `vireon_validation` Package

### 3.1 `vireon_validation.statistics.framework`
```python
def lin_concordance_correlation(x: np.ndarray, y: np.ndarray) -> float:
    """Compute Lin's Concordance Correlation Coefficient (CCC)."""
    ...
```

### 3.2 `vireon_validation.statistics.icc`
```python
def intraclass_correlation(data: np.ndarray, icc_type: str = "ICC(3,1)") -> float:
    """Compute Shrout & Fleiss (1979) Intraclass Correlation Coefficient (ICC)."""
    ...
```

### 3.3 `vireon_validation.benchmarks.matrix`
```python
class BenchmarkMatrix:
    """Automated perturbation stress testing matrix."""
    def __init__(self, seed: int = 42): ...
    def add_method(self, method: Any): ...
    def add_dataset(self, name: str, data: np.ndarray, labels: np.ndarray): ...
    def add_perturbation(self, perturbation: Any): ...
    def execute_matrix(腹) -> List[Dict[str, Any]]: ...
```

---

## 4. `vireon_evidence` Package

### 4.1 `vireon_evidence.registry.core`
```python
class EvidenceRegistry:
    """SQLite-backed evidence bundle registry."""
    def __init__(self, db_path: str = "evidence_registry.db"): ...
    def register(self, bundle: Any): ...
    def retrieve(self, evidence_hash: str) -> Optional[EvidenceBundle]: ...
    def list_bundles(self) -> List[Dict[str, Any]]: ...
```

### 4.2 `vireon_evidence.graph.core`
```python
class EvidenceGraph:
    """Graph database tracking relationships between EvidenceBundles, Methods, and Datasets."""
    ...
```

---

## 5. `vireon_corpus` Package

### 5.1 `vireon_corpus.dataset_manager`
```python
class DatasetManager:
    """Unified dataset manager for downloading, caching, and accessing real EEG datasets."""
    def __init__(self, cache_dir: Optional[str] = None): ...
    def list_datasets(self) -> List[str]: ...
    def get_dataset_info(self, key: str) -> Dict[str, Any]: ...
    def load_dataset(self, key: str, seed: int = 42) -> Dict[str, Any]: ...
```

---

## Detailed Method Signatures & Type Annotations

```python
# Helper functions for dataset conversion
def array_to_signal(arr: np.ndarray, fs: float = 250.0, names: Optional[List[str]] = None) -> ISignal:
    """Convert numpy array into ISignal contract object."""
    ...

def signal_to_array(sig: ISignal) -> np.ndarray:
    """Extract raw numpy array from ISignal object."""
    ...
```

```python
# Perturbation Library Types
class WhiteNoisePerturbation:
    def __init__(self, name: str = "WhiteNoise", severity: float = 0.5, seed: int = 42): ...
    def apply(self, X: np.ndarray) -> np.ndarray: ...

class LineNoisePerturbation:
    def __init__(self, severity: float = 0.8, freq: float = 60.0): ...
    def apply(self, X: np.ndarray) -> np.ndarray: ...

class ChannelDropoutPerturbation:
    def __init__(self, name: str = "ChannelDropout", severity: float = 0.2): ...
    def apply(self, X: np.ndarray) -> np.ndarray: ...
```

```python
# Exporter Modules
class MultiFormatReportGenerator:
    def __init__(self, bundle: EvidenceBundle): ...
    def generate_markdown(self) -> str: ...
    def generate_json(self) -> str: ...
    def generate_latex(self) -> str: ...
```

---

## 6. Code Usage Examples for All 22 Algorithms

### 6.1 `VireonCSP`
```python
from vireon_methods.spatial.vireon_csp import VireonCSP
import numpy as np

X = np.random.randn(40, 8, 250)
y = np.array([0, 1] * 20)
csp = VireonCSP(n_components=4)
features = csp.fit_transform(X, y)
assert features.shape == (40, 4)
```

### 6.2 `VireonWelch`
```python
from vireon_methods.spectral.vireon_welch import VireonWelch
import numpy as np

signal = np.random.randn(1000)
welch = VireonWelch(fs=250.0, nperseg=256)
freqs, psd = welch.compute(signal)
```

### 6.3 `VireonMultitaper`
```python
from vireon_methods.spectral.vireon_multitaper import VireonMultitaper
import numpy as np

signal = np.random.randn(1000)
mt = VireonMultitaper(fs=250.0, NW=3.0, n_tapers=5)
freqs, psd = mt.compute(signal)
```

### 6.4 `VireonSTFT`
```python
from vireon_methods.spectral.vireon_stft import VireonSTFT
import numpy as np

signal = np.random.randn(1000)
stft = VireonSTFT(fs=250.0, nperseg=128)
f, t, spec = stft.compute(signal)
```

### 6.5 `VireonWavelet`
```python
from vireon_methods.spectral.vireon_wavelets import VireonWavelet
import numpy as np

signal = np.random.randn(1000)
wavelet = VireonWavelet(fs=250.0, frequencies=np.arange(1, 50))
tf_matrix = wavelet.compute(signal)
```

### 6.6 `VireonICA`
```python
from vireon_methods.spatial.vireon_ica import VireonICA
import numpy as np

X = np.random.randn(40, 8, 250)
ica = VireonICA(n_components=4)
components = ica.fit_transform(X)
```

### 6.7 `VireonWPLI`
```python
from vireon_methods.connectivity.vireon_connectivity import VireonWPLI
import numpy as np

data = np.random.randn(2, 1000)
wpli = VireonWPLI().compute(data, fs=250.0, band=(8.0, 12.0))
```

### 6.8 `VireonAEC`
```python
from vireon_methods.connectivity.vireon_connectivity import VireonAEC
import numpy as np

data = np.random.randn(8, 1000)
aec_mat = VireonAEC().compute(data, fs=250.0, band=(8.0, 12.0))
```

### 6.9 `VireonLCMV`
```python
from vireon_methods.source_localization.vireon_beamforming import VireonLCMV
import numpy as np

leadfield = np.random.randn(8, 100)
lcmv = VireonLCMV(leadfield=leadfield)
sources = lcmv.fit_transform(np.random.randn(8, 1000))
```

### 6.10 `VireonMinimumNorm`
```python
from vireon_methods.source_localization.vireon_source_localization import VireonMinimumNorm
import numpy as np

leadfield = np.random.randn(8, 100)
mne = VireonMinimumNorm(leadfield=leadfield)
sources = mne.fit_transform(np.random.randn(8, 1000))
```

### 6.11 `VireonEMD`
```python
from vireon_methods.time_frequency.vireon_emd import VireonEMD
import numpy as np

sig = np.random.randn(300)
emd = VireonEMD(max_imfs=4)
imfs = emd.fit_transform(sig)
```

### 6.12 `VireonConvolution`
```python
from vireon_methods.signal_processing.vireon_convolution import VireonConvolution
import numpy as np

x = np.random.randn(100)
h = np.random.randn(10)
conv = VireonConvolution(mode="full")
y = conv.convolve(x, h)
```

### 6.13 `VireonRiemannianMDM`
```python
from vireon_methods.spatial.vireon_riemannian import VireonRiemannianMDM
import numpy as np

X = np.random.randn(20, 4, 100)
y = np.array([0, 1] * 10)
mdm = VireonRiemannianMDM()
preds = mdm.fit_transform(X, y)
```

### 6.14 `VireonxDAWN`
```python
from vireon_methods.spatial.vireon_xdawn import VireonxDAWN
import numpy as np

X = np.random.randn(20, 4, 100)
y = np.array([0, 1] * 10)
xdawn = VireonxDAWN(n_filter=2)
xdawn.fit(X, y)
proj = xdawn.transform(X)
```

### 6.15 `VireonFBCSP`
```python
from vireon_methods.spatial.vireon_fbcsp import VireonFBCSP
import numpy as np

X = np.random.randn(20, 4, 100)
y = np.array([0, 1] * 10)
fbcsp = VireonFBCSP(n_components=2)
feats = fbcsp.fit_transform(X, y)
```

### 6.16 `EEGNetWrapper`
```python
from vireon_methods.deep_learning.eegnet import EEGNetWrapper
import numpy as np

X = np.random.randn(20, 4, 100)
y = np.array([0, 1] * 10)
net = EEGNetWrapper(n_classes=2, channels=4, samples=100)
preds = net.predict(X)
```

### 6.17 `DeepConvNetWrapper`
```python
from vireon_methods.deep_learning.deepconvnet import DeepConvNetWrapper
import numpy as np

X = np.random.randn(20, 4, 100)
y = np.array([0, 1] * 10)
net = DeepConvNetWrapper(n_classes=2, channels=4, samples=100)
preds = net.predict(X)
```

### 6.18 `VireonWaveletCoherence`
```python
from vireon_methods.connectivity.vireon_wavelet_coherence import VireonWaveletCoherence
import numpy as np

wc = VireonWaveletCoherence()
coh = wc.compute(np.random.randn(4, 100))
```

### 6.19 `VireonTransferEntropy`
```python
from vireon_methods.connectivity.vireon_transfer_entropy import VireonTransferEntropy
import numpy as np

te = VireonTransferEntropy()
score = te.compute(np.random.randn(100), np.random.randn(100))
```

### 6.20 `VireonMutualInformation`
```python
from vireon_methods.connectivity.vireon_mutual_information import VireonMutualInformation
import numpy as np

mi = VireonMutualInformation()
score = mi.compute(np.random.randn(100), np.random.randn(100))
```

### 6.21 `lin_concordance_correlation`
```python
from vireon_validation.statistics.framework import lin_concordance_correlation
import numpy as np

x = np.random.randn(100)
y = x + np.random.randn(100) * 0.01
ccc = lin_concordance_correlation(x, y)
```

### 6.22 `intraclass_correlation`
```python
from vireon_validation.statistics.icc import intraclass_correlation
import numpy as np

data = np.random.randn(20, 3)
icc = intraclass_correlation(data, icc_type="ICC(3,1)")
```

---

## Appendix: Version History & Deprecations
- **v0.1.0**: Core contracts and initial CSP/Welch methods.
- **v0.5.0**: Validation suite and initial evidence graph.
- **v0.5.1**: FFT-based convolution, MNE minimum norm/beamformer cross-validation, ICC statistics.
- **v0.6.0**: 22 literature reproductions, 13 examples, corporate/regulatory audit binders.
- **v1.0.0**: 8 new algorithms (Riemannian, xDAWN, FBCSP, EEGNet, DeepConvNet, Wavelet Coherence, TE, MI), unified DatasetManager, PyPI installer, Docker container, MkDocs site.
