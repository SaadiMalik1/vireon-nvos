### Acceptance Criteria Checklist
- [x] `csp_vir` is `CSPPlugin`, not `mne.decoding.CSP`.
- [x] Feature shapes match: `(n_epochs, 2*n_components)`.
- [x] Correlation between Vireon and MNE features > 0.9 (after permutation matching).

### Verification Output
- Pytest passed with `CSPPlugin`.
