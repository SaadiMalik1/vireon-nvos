### Acceptance Criteria Checklist
- [x] Deleted `SeizureDetectionWorkflow` (`grep` returns 0).
- [x] No import errors (`vireon-lab` tests pass).
- [x] Dead workflow removed.

### Verification Output
`pytest vireon-lab/tests/` passed (9 passed). `rg "SeizureDetectionWorkflow"` returns 0.
