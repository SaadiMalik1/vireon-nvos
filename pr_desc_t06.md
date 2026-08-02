### Acceptance Criteria Checklist
- [x] git_sha is 40-char hex or None.
- [x] dependency_versions dict has numpy, scipy, sklearn, mne, pydantic.
- [x] os_info, cpu_info, compiler_info non-None.
- [x] blas_implementation non-None.
- [x] environment_fingerprint is 64-char hex, NOT "deterministic-virtual-env".
- [x] Same env → same fingerprint (deterministic).
- [x] rg "deterministic-virtual-env" returns 0.

### Verification Output
- Pytest passed.
- Python verification script output:
  - git_sha: cbd7d65ccb171cd0e317554a481dfe121440cc06
  - blas: openblas64__openblas
  - fingerprint: 51fc43146fbcffb4 ...
