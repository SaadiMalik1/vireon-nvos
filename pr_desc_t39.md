### Acceptance Criteria Checklist
- [x] `verify_checksum()` reads `checksums.sha256` if `expected_checksum` is None.
- [x] Computes real SHA-256 in chunks (to support large files).
- [x] Returns False if mismatch, True if all match.
- [x] Implemented in all 3 plugins (`EEGBCIPlugin`, `ERPCOREPlugin`, `SleepEDFPlugin`).

### Verification Output
- Test in `test_checksum.py` verifies both `checksums.sha256` reading and explicit single-file hashing, as well as failure when files are altered.
