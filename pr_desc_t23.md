### Acceptance Criteria Checklist
- [x] `method.execute()` is called.
- [x] CCC is computed from real results.
- [x] Runtime is measured.
- [x] `hash_checksum` is a real SHA-256.
- [x] `success=False` when `method.execute()` raises.
- [x] `error` field populated on failure.
- [x] `rg "ccc.*0\.95" vireon-validation/` returns 0.
- [x] `rg "10\.mock\.doi" vireon-validation/` returns 0.

### Verification Output
- Pytest passed with coverage >= 90%.
- `rg` checks passed.
