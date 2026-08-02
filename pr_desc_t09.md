### Acceptance Criteria Checklist
- [x] `VireonWelch(fs=250, nperseg=512).compute(signal)` returns `(f, psd)` tuple.
- [x] `f` is a 1-D array of length `nperseg//2 + 1`.
- [x] `psd` is a 1-D array of the same length.
- [x] `np.allclose(psd_vireon, psd_scipy, rtol=1e-7)` passes.
- [x] NaN input raises.
- [x] Signal shorter than `nperseg` raises.
- [x] No `np.random` calls.
- [x] `native/spectral.py::VireonWelch` raises `NotImplementedError`.

### Verification Output
- Pytest passed.
- Python verification snippet outputs `Welch matches scipy to 1e-7`.
