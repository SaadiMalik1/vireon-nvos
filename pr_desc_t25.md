### Acceptance Criteria Checklist
- [x] Test imports `VireonWelch` (not `vireon_validation.metrics.compute_psd`).
- [x] No `psd / np.sum(psd)` normalization.
- [x] `np.allclose(psd_v, psd_s, rtol=1e-7)` passes.
- [x] Test fails if `VireonWelch` is broken.

### Verification Output
- Pytest passed with absolute PSD comparison against SciPy.
