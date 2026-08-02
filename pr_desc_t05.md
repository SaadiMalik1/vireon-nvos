### Acceptance Criteria Checklist
- [x] Different bundle contents → different hashes.
- [x] Same bundle → same hash (deterministic).
- [x] Tampered bundle → verify_integrity returns False.
- [x] No "# Stubbed" comment.
- [x] pytest passes.

### Verification Output
- 3/3 tests passed.
- rg "# Stubbed" vireon-evidence/ returned 0 matches.
