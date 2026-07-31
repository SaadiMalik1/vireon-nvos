# vireon-methods

`vireon-methods` contains the core analytical algorithms used to decode or process neuro-data.

## Standard Methodologies
1. **DSP**: Welch PSD, Multitaper, FIR/IIR Filters.
2. **Spatial Filters**: Common Spatial Pattern (CSP), Independent Component Analysis (ICA).
3. **Machine Learning**: Linear Discriminant Analysis (LDA), Bayesian Classifiers.

Every method in this repository is heavily constrained by a `ScientificContract`. If a user attempts to run a non-stationary signal through the `Welch PSD` plugin, `vireon-core` will block the execution.

## Status
- **DSP**: [FULLY IMPLEMENTED] Welch PSD, Notch, Bandpass filters are functional.
- **Spatial Filters**: [STUBBED] CSP and ICA contracts exist, but the native solvers are pending.
- **Machine Learning**: [STUBBED] Decoders are currently placeholders pending Phase F execution.