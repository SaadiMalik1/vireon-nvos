### Acceptance Criteria Checklist
- [x] rg "_raw_provider_data" returns 0 in vireon-core and vireon-validation.
- [x] EvidenceGenerator.generate_bundle accepts raw_provider_data parameter.
- [x] telemetry.npz still written and hashed.
- [x] IEvidence instances have no _raw_provider_data attr after execution.
- [x] pytest passes.

### Verification Output
- Pytest passed for T07 tests and Reproducibility tests.
- rg `_raw_provider_data` returns 0.
