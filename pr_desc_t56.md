### Acceptance Criteria Checklist
- [x] Deleted `MethodologicalValidator` (`grep` returns 0).
- [x] No duplicate methodology validators.
- [x] All 50 tests in `vireon-validation` pass.

### Verification Output
`pytest vireon-validation/tests/` passed (50 passed). `rg "MethodologicalValidator" vireon-validation/` returns 0.
