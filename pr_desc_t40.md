### Acceptance Criteria Checklist
- [x] `verify_checksum()` returns `False` for a tampered file (Tested in T39).
- [x] `verify_checksum()` returns `True` for an unmodified file (Tested in T39).
- [x] `generate_hash()` returns a 64-char hex string.
- [x] `generate_hash()` returns different values for different datasets.
- [x] `rg "mock_hash" vireon-corpus/` returns 0.
- [x] `rg "return True" vireon-corpus/` in `verify_checksum` returns 0.

### Verification Output
- Test in `test_hash.py` verifies different datasets yield different hashes and `mock_hash` strings are removed.
