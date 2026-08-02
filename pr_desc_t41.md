### Acceptance Criteria Checklist
- [x] `rg "SRL_5" vireon-corpus/` returns 0.
- [x] `rg "SRL_1" vireon-corpus/` returns >= 3.
- [x] `validate_srl_claim` returns violations for unsupported SRL_4+ claims.

### Verification Output
- Downgraded `EEGBCIPlugin`, `ERPCOREPlugin`, and `SleepEDFPlugin` SRLs to `SRL_1`.
- Added `validate_srl_claim` to `srl_automation.py` with passing unit tests.
