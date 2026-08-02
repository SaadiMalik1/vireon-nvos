### Acceptance Criteria Checklist
- [x] `provider: eegbci` in experiment returns `EEGBCIProvider` with real download attempt.
- [x] `EEGBCIProvider` is imported and used in `base.py`.
- [x] If data is not downloaded, it raises `FileNotFoundError` (honest failure).

### Verification Output
- Test in `test_eegbci_provider.py` passes and correctly asserts that `FileNotFoundError` is raised.
