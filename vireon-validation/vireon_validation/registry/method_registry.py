from pydantic import BaseModel
from typing import Dict, List, Optional

class ReferenceImplementation(BaseModel):
    name: str
    version: str
    expected_tolerances: Dict[str, float]
    computational_complexity: str
    failure_modes: List[str]
    numerical_assumptions: List[str]
    supported_modalities: List[str]

class CanonicalMethod(BaseModel):
    method_name: str
    description: str
    reference_papers: List[str]
    benchmark_datasets: List[str]
    implementations: Dict[str, ReferenceImplementation]

class MethodRegistry:
    """
    Canonical registry of every reference implementation.
    """
    _registry: Dict[str, CanonicalMethod] = {}

    @classmethod
    def register(cls, method: CanonicalMethod):
        cls._registry[method.method_name] = method
        
    @classmethod
    def get(cls, method_name: str) -> Optional[CanonicalMethod]:
        return cls._registry.get(method_name)

# --- Pre-populate registry with milestone requirements ---

welch_method = CanonicalMethod(
    method_name="Welch PSD",
    description="Welch's method for estimating power spectral density.",
    reference_papers=["Welch, P. (1967). The use of fast Fourier transform for the estimation of power spectra..."],
    benchmark_datasets=["Synthetic", "EEGBCI", "CHB-MIT", "SleepEDF", "ERP CORE"],
    implementations={
        "SciPy": ReferenceImplementation(
            name="scipy.signal.welch",
            version="1.10.1",
            expected_tolerances={"rmse": 1e-7, "mae": 1e-7},
            computational_complexity="O(N log N)",
            failure_modes=["Window length > signal length", "Zero-variance signal"],
            numerical_assumptions=["Stationary signal over window"],
            supported_modalities=["EEG", "MEG", "ECG"]
        ),
        "MNE": ReferenceImplementation(
            name="mne.time_frequency.psd_welch",
            version="1.4.0",
            expected_tolerances={"rmse": 1e-6},
            computational_complexity="O(N log N)",
            failure_modes=["NaNs in data"],
            numerical_assumptions=["Proper scaling to V^2/Hz"],
            supported_modalities=["EEG", "MEG"]
        )
    }
)
MethodRegistry.register(welch_method)

csp_method = CanonicalMethod(
    method_name="CSP",
    description="Common Spatial Patterns for feature extraction.",
    reference_papers=["Koles, Z. J. (1991). The quantitative extraction and topographic mapping..."],
    benchmark_datasets=["Synthetic", "EEGBCI", "CHB-MIT", "ERP CORE"],
    implementations={
        "MNE": ReferenceImplementation(
            name="mne.decoding.CSP",
            version="1.4.0",
            expected_tolerances={"rmse": 1e-5},
            computational_complexity="O(C^3)",
            failure_modes=["Rank deficient covariance"],
            numerical_assumptions=["Positive definite covariance matrices"],
            supported_modalities=["EEG", "MEG"]
        ),
        "pyRiemann": ReferenceImplementation(
            name="pyriemann.spatialfilters.CSP",
            version="0.3.0",
            expected_tolerances={"rmse": 1e-5},
            computational_complexity="O(C^3)",
            failure_modes=["Singular matrices"],
            numerical_assumptions=["SPD matrices"],
            supported_modalities=["EEG", "MEG"]
        )
    }
)
MethodRegistry.register(csp_method)

ica_method = CanonicalMethod(
    method_name="ICA",
    description="Independent Component Analysis.",
    reference_papers=["Hyvärinen, A., & Oja, E. (2000). Independent component analysis..."],
    benchmark_datasets=["Synthetic", "EEGBCI", "CHB-MIT", "SleepEDF"],
    implementations={
        "scikit-learn": ReferenceImplementation(
            name="sklearn.decomposition.FastICA",
            version="1.2.2",
            expected_tolerances={"rmse": 1e-4},
            computational_complexity="O(N C^2)",
            failure_modes=["Fails to converge"],
            numerical_assumptions=["Non-Gaussian sources"],
            supported_modalities=["EEG", "MEG"]
        )
    }
)
MethodRegistry.register(ica_method)
