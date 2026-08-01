### Acceptance Criteria Checklist
- [x] `BEMModel.compute_leadfield` returns a real leadfield when MNE is installed (no RuntimeError).
- [x] `PatientSpecificModel.compute_leadfield` raises ImportError instead of RuntimeError.

### Verification Output
Checked `rg "np\.random|# Stub|pass$|return 0\.\d+"` - no unauthorized stubs.
