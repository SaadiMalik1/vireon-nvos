### Acceptance Criteria Checklist
- [x] `n_components` parameter accepted and respected.
- [x] Extract log-variance features.
- [x] Downgrade SRL to `SRL_2`.
- [x] Add `norm_trace` parameter and normalize covariance by trace if True.
- [x] No `np.random` used.

### Verification Output
- Pytest passed with coverage >= 90%.
- `rg` for `np.random` returned 0 matches in `csp.py`.
