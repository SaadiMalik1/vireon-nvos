# VIREON VGA Tracker — Validation Platform GA

**Playbook:** `imp4/vga-milestone-playbook.md`  
**Target:** `v0.5.0-validation-platform-ga`  
**Progress:** 0 / 30 Tasks Completed, 0 / 15 Criteria Verified

---

## Workstream F — Fix All Audit Findings
- [x] F01: Generate validation report (run script, commit `reports/`)
- [x] F02: Add PhysioNet download to CI
- [x] F03: Fix Tutorial 02 (3 broken imports)
- [x] F04: Fix Tutorial 03 (non-existent function)
- [x] F05: Add scipy.signal.stft comparison for VireonSTFT
- [x] F06: Add scipy.signal.cwt comparison for VireonWavelet
- [ ] F07: Add sklearn.FastICA head-to-head for VireonICA
- [ ] F08: Add mne.beamformer/mne.minimum_norm comparison
- [ ] F09: Add mne_connectivity comparison for connectivity metrics
- [ ] F10: Compute CCC in validation suite + reconcile release notes

## Workstream G — New Algorithms + Validations
- [ ] F11: Implement multitaper PSD (`vireon_multitaper.py`)
- [ ] F12: Implement empirical mode decomposition (`vireon_emd.py`)
- [ ] F13: Implement convolution/correlation (`vireon_convolution.py`)
- [ ] F14: Add real-time streaming validation scenario
- [ ] F15: Add multi-session validation (test-retest reliability)
- [ ] F16: Add cross-subject generalization validation
- [ ] F17: Add adversarial robustness validation (Martinovic P300 attack)
- [ ] F18: Add new algorithms to validation suite + report

## Workstream H — Infrastructure Hardening
- [ ] F19: Wire FastAPI to SQLite EvidenceRegistry
- [ ] F20: Rename DOIMinter to EvidenceIdentifier + document
- [ ] F21: Populate graph in Tutorial 04
- [ ] F22: Delete/implement 3 stub literature tests
- [ ] F23: Delete legacy statistics/core.py (duplicate code)
- [ ] F24: Tighten BCI competition tolerance + add NaN/Inf contract tests

## Workstream I — Integration + Polish
- [ ] F25: Generate real API reference (hand-write key sections)
- [ ] F26: Add multi-channel FFT test + high-order IIR stability
- [ ] F27: Fix NotebookGenerator embedded code cell
- [ ] F28: External researcher quickstart guide (install to publish in 1hr)
- [ ] F29: Final integration — verify G1-G15, tag `v0.5.0-validation-platform-ga`
- [ ] F30: Release verification & polish

---

## Success Criteria (G1–G15)
- [ ] G1: No self-referential tests (`rg "manual.*segmented|own.*formula" tests/test_algorithm_validation_suite/` = 0)
- [ ] G2: All algorithms have reference comparison (scipy/MNE/sklearn imported across suite)
- [x] G3: Validation report generated (`reports/algorithm_validation_report.md` > 200 lines)
- [x] G4: PhysioNet data in CI (`.github/workflows/ci.yml` downloads eegbci data)
- [x] G5: Tutorial 02 executes without ImportError
- [x] G6: Tutorial 03 executes without error
- [ ] G7: FastAPI persists to SQLite (evidence survives restart)
- [ ] G8: DOIMinter renamed honestly to EvidenceIdentifier
- [ ] G9: API reference has real content (`docs/api_reference.md` > 200 lines)
- [ ] G10: 3 new algorithms added (multitaper, EMD, convolution)
- [ ] G11: 3 new validation scenarios in `examples/`
- [ ] G12: CCC actually computed in validation suite (`rg "lin_concordance|compute_ccc" tests/test_algorithm_validation_suite/` ≥ 3)
- [ ] G13: Full test suite passes (`pytest --tb=no -q` = 0 failures)
- [ ] G14: No unseeded `np.random` in production code
- [ ] G15: All 4 tutorials execute without error

---

## Milestone Status
- Phase: Workstream F (Fix All Audit Findings)
- Tasks completed: 0 / 30
- Success criteria passing: 0 / 15
