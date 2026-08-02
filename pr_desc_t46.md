### Acceptance Criteria Checklist
- [x] `vireon_validation.decision.DecisionEngine` is renamed to `StringConstraintEvaluator`.
- [x] `vireon-lab/vireon_lab/cli/runner.py` imports `DecisionEngine` from `vireon_knowledge.decision_engine`.
- [x] Runtime decisions produce `DecisionTrace` objects (from `DecisionResult`).
- [x] No two classes named `DecisionEngine` in the codebase.

### Verification Output
All tests in `vireon-validation/tests/` and `vireon-lab/tests/` passed (59 tests passed). No unauthorized stubs or mocked returns found in modified files.
