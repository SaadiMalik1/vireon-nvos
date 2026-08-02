### Acceptance Criteria Checklist
- [x] ICC of perfectly agreeing raters ≈ 1.0.
- [x] ICC of random ratings ≈ 0.0.
- [x] ICC of systematically disagreeing raters < 0.5.
- [x] `rg "return 0\.94" vireon-validation/` returns 0.

### Verification Output
- 3 new tests in `test_icc.py` passed.
- `rg "return 0\.94"` returns nothing.
