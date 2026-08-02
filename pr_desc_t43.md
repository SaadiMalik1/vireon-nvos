### Acceptance Criteria Checklist
- [x] Make `reproduce <doi>` actually do reproduction using `ExecutionEngine`.
- [x] Remove hardcoded accuracy/fake success messages.
- [x] Compare against expected outputs with specified tolerance.
- [x] Use `vireon-publications/registry/doi_index.json` to resolve DOIs to scenarios.
- [x] Update `vireon-publications/cli.py` to use `ReproducibilityEngine`.

### Verification Output
- Verified failing reproduction matches expectations for unconfigured scenarios (honest failure).
- Automated tests pass.
