### Acceptance Criteria Checklist
- [x] Old class name no longer exists (`CHBMITProvider`).
- [x] All imports updated.
- [x] Tests pass.

### Verification Output
- `rg "CHBMITProvider" --type py` returns 0.
- `rg "SyntheticCHBMITProvider" --type py` returns 1.
