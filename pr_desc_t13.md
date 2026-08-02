### Acceptance Criteria Checklist
- [x] Components match `sklearn.decomposition.FastICA` subspace to `atol=1e-6`.
- [x] `n_components > min(n_samples, n_features)` raises.
- [x] `mixing_` property returns the mixing matrix.
- [x] Uses `DeterministicRNG` for initialization (reproducible).
- [x] NaN raises.
- [x] `native/spatial.py::VireonICA` deleted/replaced with NotImplementedError.

### Verification Output
- Pytest passed with coverage >= 90%.
- `rg` for `np.random` returned 0 matches in `vireon_ica.py`.
