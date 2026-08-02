### Acceptance Criteria Checklist
- [x] Filter coefficients match `scipy.signal.butter` to `rtol=1e-10`.
- [x] Filtered output matches `scipy.signal.filtfilt`.
- [x] NaN raises.
- [x] `native/signal.py::VireonButterworth` relabeled as "scipy wrapper" in docstring.
- [x] No `np.random` used.

### Verification Output
- Pytest passed with coverage >= 90%.
- `rg` for `np.random` returned 0 matches in `vireon_iir.py`.
