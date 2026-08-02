### Acceptance Criteria Checklist
- [x] Deleted `LiteratureVerifier` (`grep` returns 0).
- [x] No `AttributeError`-prone code referencing non-existent `_graph`.
- [x] All 50 tests in `vireon-validation` pass.

### Verification Output
`pytest vireon-validation/tests/` passed (50 passed). `rg "LiteratureVerifier" vireon-validation/` returns 0.
