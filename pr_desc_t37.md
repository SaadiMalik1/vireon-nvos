### Acceptance Criteria Checklist
- [x] `provider: physionet_mi` in experiment returns `PhysioNetMotorImageryProvider` with real download attempt.
- [x] `PhysioNetMotorImageryProvider` is imported and used in `base.py`.
- [x] If data is not downloaded, it raises `FileNotFoundError` (honest failure).

### Verification Output
- Test in `test_physionet_provider.py` passes and correctly asserts that `FileNotFoundError` is raised.
