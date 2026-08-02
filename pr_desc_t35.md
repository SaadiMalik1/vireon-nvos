### Acceptance Criteria Checklist
- [x] Old class name no longer exists (`SleepEDFProvider`).
- [x] All imports updated.
- [x] Tests pass.

### Verification Output
- `rg "SleepEDFProvider" --type py` returns 0.
- `rg "SyntheticSleepEDFProvider" --type py` returns 1.
