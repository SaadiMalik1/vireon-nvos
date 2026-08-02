### Acceptance Criteria Checklist
- [x] np.allclose(np.abs(Zxx_vireon), np.abs(Zxx_scipy), rtol=1e-7) passes.
- [x] Zxx is complex (not just magnitude).
- [x] f and t axes are correct.
- [x] NaN raises.
- [x] native/spectral.py::VireonSTFT deleted/replaced with NotImplementedError.

### Verification Output
- Pytest passed with coverage >= 90%.
- No `np.random` used in `vireon_stft.py`.
