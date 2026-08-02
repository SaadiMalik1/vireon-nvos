### Acceptance Criteria Checklist
- [x] rg "expected_side_channel_leak" vireon-core/ returns 0.
- [x] rg "p300_detected" vireon-core/ returns 0.
- [x] AssertionEvaluator ABC exists in contracts/base.py.
- [x] DefaultAssertionEvaluator handles numeric/bool/string.
- [x] BCIAssertionEvaluator in vireon-validation handles P300.
- [x] ExecutionEngine accepts assertion_evaluator parameter.
- [x] pytest passes.

### Verification Output
- Pytest passed.
- Both `rg` commands returned 0 matches in `vireon-core/`.
