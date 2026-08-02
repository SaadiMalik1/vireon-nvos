### Acceptance Criteria Checklist
- [x] `FailureAtlas` uses SQLite for persistence.
- [x] Failures survive process restart.
- [x] `db_path` parameter is actually used.
- [x] `list_failures(method_id)` filters by method.

### Verification Output
`pytest vireon-evidence/tests/test_failure_atlas.py` passed (2 passed). All tests in `vireon-evidence` passed.
