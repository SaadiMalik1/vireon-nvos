### Acceptance Criteria Checklist
- [x] `verify` subcommand accepts `--bundle <path>`.
- [x] Valid bundle exits 0.
- [x] Tampered bundle exits 1 with a clear message.
- [x] No `AttributeError`.

### Verification Output
- Automated tests `test_verify_cli.py` pass.
