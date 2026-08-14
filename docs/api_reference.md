# VIREON API Reference

Auto-generated from source.

---


## `vireon_methods.spectral.vireon_welch`


### `VireonWelch`


Native Welch PSD implementation.

Reference: Welch, P. D. (1967). The Use of Fast Fourier Transform for the 
Estimation of Power Spectra: A Method Based on Time Averaging Over Short, 
Modified Periodograms. IEEE Transactions on Audio and Electroacoustics, 15(2), 70–73.
DOI: 10.1109/TAU.1967.1161901



```python
VireonWelch(self, fs: float, nperseg: int = 256, noverlap: int = None, window: str = 'hann', detrend: str = 'constant', scaling: str = 'density')
```


## `vireon_methods.spectral.vireon_fft`


### `VireonFFT`


Native FFT / periodogram implementation.

Supports:
- Real FFT (rfft for real-valued signals)
- Windowing (hann, hamming, blackman, boxcar)
- One-sided spectrum scaling (x2 for non-DC, non-Nyquist bins)
- Power spectrum (V^2) and power spectral density (V^2/Hz)



```python
VireonFFT(self, fs: float, nfft: int = None, window: str = 'hann', detrend: str = 'constant', scaling: str = 'density')
```


## `vireon_methods.spectral.vireon_stft`


### `VireonSTFT`


Native Short-Time Fourier Transform (STFT) implementation.

Produces a complex time-frequency representation of the signal.



```python
VireonSTFT(self, fs: float, nperseg: int = 256, noverlap: int = None, window: str = 'hann', detrend: str = 'constant')
```


## `vireon_methods.spectral.vireon_wavelets`


### `VireonWavelet`


Continuous Wavelet Transform.

Supports: morlet, paul, dog (derivative of gaussian), mexh (mexican hat).
Returns complex coefficients (preserves phase).



```python
VireonWavelet(self, fs: float, frequencies: numpy.ndarray, wavelet: str = 'morlet', w: float = 6.0, m: int = 4)
```


## `vireon_methods.spectral.vireon_multitaper`


### `VireonMultitaper`


Multitaper Power Spectral Density (PSD) estimator using Slepian (DPSS) tapers.

Reference: Thomson, D. J. (1982). Spectrum estimation and harmonic analysis. 
Proceedings of the IEEE, 70(9), 1055-1096. DOI: 10.1109/PROC.1982.12433



```python
VireonMultitaper(self, fs: float, NW: float = 2.5, n_tapers: int = None)
```


## `vireon_methods.spatial.vireon_csp`


### `VireonCSP`



Native VIREON implementation of Common Spatial Patterns (CSP).
Calculates spatial filters via generalized eigenvalue decomposition.



```python
VireonCSP(self, n_components: int = 4)
```


## `vireon_methods.spatial.vireon_ica`


### `VireonICA`


Native FastICA implementation.

Reference: Hyvärinen, A., & Oja, E. (2000). Independent Component Analysis: 
Algorithms and Applications. Neural Networks, 13(4-5), 411-430.
DOI: 10.1016/S0893-6080(00)00026-5



```python
VireonICA(self, n_components: int = None, max_iter: int = 200, tol: float = 0.0001, fun: str = 'logcosh', whiten: str = 'unit-variance')
```


## `vireon_methods.spatial.vireon_fbcsp`


Filter Bank Common Spatial Pattern (FBCSP) Spatial Filter.

Reference: Ang, K. K., Chin, Z. Y., Zhang, H., & Guan, C. (2012). Filter bank common spatial pattern (FBCSP)
in brain-computer interface. Proceedings of the International Joint Conference on Neural Networks, 2390-2397.
DOI: 10.1109/IJCNN.2012.6252486



### `VireonFBCSP`


Filter Bank Common Spatial Patterns (Blankertz 2008).

Applies band-pass filters per frequency band, then runs CSP on each
band's filtered signal. Concatenates log-variance features across bands.



```python
VireonFBCSP(self, n_components: int = 2, bands: List[Tuple[float, float]] | None = None, filter_order: int = 4)
```


## `vireon_methods.spatial.vireon_xdawn`


xDAWN Spatial Filtering for Event-Related Potential (ERP) Signal Enhancement.

Reference: Rivet, B., Cecotti, H., Souloumiac, A., Maby, E., & Mattout, J. (2009). xDAWN algorithm 
to enhance evoked potentials: application to brain-computer interfaces. IEEE Transactions on Biomedical Engineering, 56(8), 2035-2043.
DOI: 10.1109/TBME.2009.2019709



### `VireonxDAWN`


xDAWN spatial filter for enhancing target signal-to-noise ratio in ERPs.


```python
VireonxDAWN(self, n_filter: int = 2)
```


## `vireon_methods.spatial.vireon_riemannian`


Riemannian Geometry Minimum Distance to Mean (MDM) Spatial Classifier.

Reference: Barachant, A., Bonnet, S., Congedo, M., & Jutten, C. (2012). Multiclass brain-computer 
interface classification by Riemannian geometry. IEEE Transactions on Biomedical Engineering, 59(4), 920-928.
DOI: 10.1109/TBME.2011.2172216



### `VireonRiemannianMDM`


Minimum Distance to Mean classifier on Riemannian manifold of SPD matrices.


```python
VireonRiemannianMDM(self)
```


## `vireon_methods.filtering.vireon_iir`


### `VireonIIR`


IIR filter (Butterworth) via bilinear transform.

Reference: Oppenheim & Schafer, Discrete-Time Signal Processing.



```python
VireonIIR(self, fs: float, cutoff: float | Tuple[float, float] | list | numpy.ndarray, btype: str = 'lowpass', order: int = 4, filter_type: str = 'butter', rp: float = 5, rs: float = 40)
```


## `vireon_methods.filtering.vireon_fir`


### `VireonFIR`


FIR filter via windowed-sinc design.

Reference: Ifeachor & Jervis, Digital Signal Processing: A Practical Approach.



```python
VireonFIR(self, fs: float, cutoff: float | Tuple[float, float] | list | numpy.ndarray, numtaps: int = 101, window: str = 'hamming', pass_zero: bool = True)
```


## `vireon_methods.connectivity.vireon_connectivity`


### `VireonAEC`


Amplitude Envelope Correlation: Pearson correlation of Hilbert envelopes.


```python
VireonAEC(self, /, *args, **kwargs)
```


### `VireonCoherence`


Magnitude-squared coherence: |Pxy|² / (Pxx * Pyy).


```python
VireonCoherence(self, /, *args, **kwargs)
```


### `VireonImaginaryCoherence`


Imaginary coherence: |imag(Pxy)| / sqrt(Pxx * Pyy).


```python
VireonImaginaryCoherence(self, /, *args, **kwargs)
```


### `VireonPLI`


Phase Lag Index: |mean(sign(imag(exp(1j*(phi_i - phi_j)))))|.


```python
VireonPLI(self, /, *args, **kwargs)
```


### `VireonPLV`


Phase Locking Value: |mean(exp(1j * (phi_i - phi_j)))|.


```python
VireonPLV(self, /, *args, **kwargs)
```


### `VireonWPLI`


Weighted Phase Lag Index.

Reference: Vinck, M. et al. (2011). An improved index of phase-synchronization
for electrophysiological data in the presence of volume-conduction, noise,
and sample-size bias. NeuroImage, 55(4), 1548-1565.
DOI: 10.1016/j.neuroimage.2011.01.055



```python
VireonWPLI(self, /, *args, **kwargs)
```


## `vireon_methods.connectivity.vireon_mutual_information`


Mutual Information Information-Theoretic Functional Connectivity Estimator.

Reference: Kraskov, A., Stogbauer, H., & Grassberger, P. (2004). Estimating mutual information.
Physical Review E, 69(6), 066138. DOI: 10.1103/PhysRevE.69.066138



### `VireonMutualInformation`


Mutual Information estimator using Kraskov k-NN method (KSG estimator).

Reference: Kraskov, Stogbauer, Grassberger (2004).
"Estimating mutual information." Phys Rev E. 69:066138.
DOI: 10.1103/PhysRevE.69.066138

Implements Estimator 1 (epsilon-ball approach).



```python
VireonMutualInformation(self, k: int = 4, n_neighbors: int | None = None, n_bins: int | None = None)
```


## `vireon_methods.deep_learning.eegnet`


EEGNet Deep Convolutional Neural Network Implementation.

Reference: Lawhern, V. J., Solon, A. J., Waytowich, N. R., Gordon, S. M., Hung, T. M., & Lance, B. J. (2018).
EEGNet: a compact convolutional neural network for EEG-based brain-computer interfaces. Journal of Neural Engineering, 15(5), 056013.
DOI: 10.1088/1741-2552/aace8c



### `EEGNetWrapper`


Production Wrapper for Lawhern 2018 EEGNet Deep Learning Architecture.


```python
EEGNetWrapper(self, n_classes: int = 2, channels: int = 8, samples: int = 250, lr: float = 0.001, batch_size: int = 16, epochs: int = 50, seed: int = 42, use_gpu: bool = True)
```


## `vireon_methods.deep_learning.deepconvnet`


DeepConvNet Deep Convolutional Neural Network Implementation.

Reference: Schirrmeister, R. T., Springenberg, J. T., Fiederer, L. D. J., Glasstetter, M., Eggensperger, K., Tangermann, M., Hutter, F., Burgard, W., & Ball, T. (2017).
Deep learning with convolutional neural networks for EEG decoding and visualization. Human Brain Mapping, 38(11), 5391-5420.
DOI: 10.1002/hbm.23730



### `DeepConvNetWrapper`


Production Wrapper for Schirrmeister 2017 DeepConvNet Deep Learning Architecture.


```python
DeepConvNetWrapper(self, n_classes: int = 2, channels: int = 8, samples: int = 250, lr: float = 0.001, batch_size: int = 16, epochs: int = 50, seed: int = 42, use_gpu: bool = True)
```


## `vireon_core.contracts.evidence`


### `DatasetProvenance`


```python
DatasetProvenance(self, /, **data: 'Any') -> 'None'
```


### `EnvironmentFingerprint`


```python
EnvironmentFingerprint(self, /, **data: 'Any') -> 'None'
```


### `EvidenceBundle`



Evidence Bundle 5.0 (Scientific Ecosystem & Regulatory Readiness)



```python
EvidenceBundle(self, /, **data: 'Any') -> 'None'
```


### `MethodProvenance`


```python
MethodProvenance(self, /, **data: 'Any') -> 'None'
```


### `RegulatoryProfile`


```python
RegulatoryProfile(self, /, **data: 'Any') -> 'None'
```


### `SoftwareProvenance`


```python
SoftwareProvenance(self, /, **data: 'Any') -> 'None'
```


## `vireon_core.contracts.plugin`


### `ContractValidator`


```python
ContractValidator(self, /, *args, **kwargs)
```


### `IDatasetPlugin`



Plugin interface for acquiring and formatting canonical validation datasets.



```python
IDatasetPlugin(self, /, *args, **kwargs)
```


### `IMethodPlugin`



Plugin interface for scientific methods (Signal Processing, ML, etc).



```python
IMethodPlugin(self, /, *args, **kwargs)
```


### `IPlugin`



Capability-based interface for all VIREON plugins.
The kernel routes IScientificObjects based on capabilities.



```python
IPlugin(self, /, *args, **kwargs)
```


### `PluginCapability`


```python
PluginCapability(self, /, **data: 'Any') -> 'None'
```


### `ScientificContract`


```python
ScientificContract(self, /, **data: 'Any') -> 'None'
```


### `ScientificContractViolation`



Raised when a plugin's execution violates its declared Scientific Contract
(e.g., input data violates mathematical assumptions or numerical tolerances).



```python
ScientificContractViolation(self, plugin_id: str, violated_assumption: str, details: str, remediation: str)
```


### `ScientificReadinessLevel`


```python
ScientificReadinessLevel(self, /, *args, **kwargs)
```


## `vireon_evidence.registry.core`


### `EvidenceRegistry`


Evidence Registry with SQLite backend for persisting and querying evidence bundles.

Uses append-only INSERT OR IGNORE semantics to prevent silent overwrites.



```python
EvidenceRegistry(self, db_path: str = 'evidence_registry.db')
```


## `vireon_evidence.graph.core`


### `EvidenceGraph`



The Scientific Evidence Graph with optional SQLite persistence.
Uses networkx to store nodes (datasets, methods, evidence bundles, claims) and directed edges (relationships).



```python
EvidenceGraph(self, db_path: str | None = None)
```


## `vireon_corpus.dataset_manager`


Unified Dataset Manager for Real EEG Ingestion via MNE & Disk Caching.


### `DatasetManager`


Manages real EEG data downloading, MNE ingestion, caching, and verification.


```python
DatasetManager(self, cache_dir: str | None = None)
```


## `vireon_knowledge.engine`


### `KnowledgeGraph`



A lightweight inference engine that parses the JSON-LD scientific knowledge graph
to evaluate hypotheses and generate evidence-backed recommendations.



```python
KnowledgeGraph(self, knowledge_root: str | None = None)
```
