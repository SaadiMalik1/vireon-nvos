### Acceptance Criteria Checklist
- [x] Filter coefficients match `scipy.signal.firwin` to `rtol=1e-10`.
- [x] Filtered output matches `scipy.signal.filtfilt(data, coeffs)`.
- [x] NaN raises.
- [x] `native/filtering.py::VireonFIR` mock replaced with NotImplementedError.
- [x] No `np.random` used.

### Verification Output
- Pytest passed with coverage >= 90%.
- `rg` for `np.random` returned 0 matches in `vireon_fir.py`.
