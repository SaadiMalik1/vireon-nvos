### Acceptance Criteria Checklist
- [x] Old class name no longer exists (`BCICompetitionIV2aProvider`).
- [x] All imports updated.
- [x] Tests pass.

### Verification Output
- `rg "BCICompetitionIV2aProvider" --type py` returns 0.
- `rg "SyntheticBCICompetitionProvider" --type py` returns 1.
