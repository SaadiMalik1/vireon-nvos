# VIREON Tutorial 02: Algorithm Validation

Learn how to validate custom algorithms against canonical scientific reference libraries (SciPy, MNE, scikit-learn) with rigorous statistical tolerances.

## Statistical Rigor Framework

VIREON enforces numerical cross-validation using:
1. **Concordance Correlation Coefficient (CCC)**: Measures agreement on a 45-degree line.
2. **Root Mean Square Error (RMSE)**: Quantifies deviation magnitude.
3. **Bootstrap Confidence Intervals (95% CI)**: Quantifies metric uncertainty without distributional assumptions.
4. **Permutation Testing**: Non-parametric significance testing against null hypotheses.

## Validating Welch PSD against SciPy

```python
import numpy as np
import scipy.signal
from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.signal_processing.psd import WelchPSDPlugin
from vireon_validation.statistics.framework import lin_concordance_correlation
from vireon_validation.statistics.bootstrap import compute_bootstrap_ci

# Generate synthetic EEG segment
rng = DeterministicRNG(seed=1234)
fs = 250.0
t = np.arange(1000) / fs
data = np.sin(2 * np.pi * 10 * t) + rng.normal(0, 0.5, 1000)

# Compute native PSD
plugin = WelchPSDPlugin(fs=fs, nperseg=256)
f_native, psd_native = plugin.compute_psd(data)

# Compute reference PSD
f_ref, psd_ref = scipy.signal.welch(data, fs=fs, nperseg=256)

# Verify concordance
ccc = lin_concordance_correlation(psd_native, psd_ref)
ci_low, ci_high = compute_bootstrap_ci(psd_native, psd_ref, metric_fn=lin_concordance_correlation, n_bootstraps=500, seed=1234)

print(f"CCC: {ccc:.6f}")
print(f"95% CI: [{ci_low:.6f}, {ci_high:.6f}]")
assert ccc > 0.9999, "Validation failed tolerance!"
```
