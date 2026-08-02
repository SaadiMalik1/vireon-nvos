### Acceptance Criteria Checklist
- [x] Output shape `(n_sources, n_samples)`.
- [x] Localizes known source correctly.
- [x] NaN raises.
- [x] `native/imaging.py::VireonLCMV` replaced with `NotImplementedError`.
- [x] No `np.random` used.

### Verification Output
- Pytest passed with coverage >= 90%.
- `rg` for `np.random` returned 0 matches in `vireon_beamforming.py`.
