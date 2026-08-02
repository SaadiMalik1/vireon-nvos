### Acceptance Criteria Checklist
- [x] `DigitalTwinProvider` uses `SphereModel`, not `LeadfieldProjector`.
- [x] `SphereModel` is imported at runtime in `datasets.py`.
- [x] Leadfield output is in plausible range (verified via unit tests).
- [x] `LeadfieldProjector` renamed to `RandomMixingMatrix` with a docstring warning.

### Verification Output
Unit tests pass. `rg "np\.random|# Stub|pass$|return 0\.\d+"` returned no unauthorized stubs in modified files.
