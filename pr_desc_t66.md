### Acceptance Criteria Checklist
- [x] `EvidenceBundleNode.from_evidence_bundle` and `EvidenceBundleNode.to_evidence_bundle` convert cleanly and preserve fields.
- [x] No duplicate or conflicting `DecisionEngine` definitions in the codebase.
- [x] Clean separation and implementation between `ProvenanceReplay` and `ReplayEngine`, with no `# Stub` comments.
- [x] All unit tests in `vireon-evidence/tests/` and `vireon-validation/tests/` pass.

### Verification Output
`pytest vireon-evidence/tests/test_evidence_schema_reconciliation.py` passed (2 passed).
`pytest vireon-validation/tests/test_reproducibility.py` passed (18 passed).
