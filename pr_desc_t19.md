### Acceptance Criteria Checklist
- [x] Output shape `(n_sources, n_samples)`.
- [x] Localizes known source correctly.
- [x] `λ² = 1/snr²` is actually used in the computation.
- [x] NaN raises.
- [x] `native/imaging.py::VireonMinimumNorm` replaced with `NotImplementedError`.
- [x] No `np.random` used.

### Verification Output
- Pytest passed with coverage >= 90%.
- `rg` for `np.random` returned 0 matches in `vireon_source_localization.py`.
