# VIREON Remediation Tracker

## Status Legend
- [ ] Not started
- [~] In progress
- [x] Done
- [!] Blocked (see BLOCKED.md)
- [-] Deferred (cut from sprint)

## P0-CORE
- [x] T01: Plugin discovery
- [x] T02: DAG execution engine
- [x] T03: Wire decoder
- [x] T04: Contract validator
- [x] T05: Transaction content hash
- [x] T06: Real environment capture
- [x] T07: Remove side-channel
- [x] T08: Remove hardcoded domain logic

## P0-METHODS
- [x] T09: Real welch
- [x] T10: Real fft
- [x] T11: Real stft
- [x] T12: Real wavelets
- [x] T13: Real ica
- [x] T14: Fix CSP plugin
- [x] T15: Delete native mocks
- [x] T16: Real FIR filter
- [x] T17: Real IIR filter
- [x] T18: Real LCMV beamforming
- [x] T19: Real source localization
- [x] T20: Real connectivity
- [x] T21: Implement wPLI
- [x] T22: Fix Laplacian REST

## P0-VALIDATION
- [x] T23: Real benchmark matrix
- [x] T24: Fix CSP crossval
- [x] T25: Fix PSD crossval
- [x] T26: Real ERP p300 test
- [x] T27: Real seizure test
- [x] T28: Real BCI competition test
- [x] T29: Real sleep staging test
- [x] T30: Real ICC
- [x] T31: Implement Passing-Bablok
- [x] T32: Implement MCC

## P0-CORPUS + CLI
- [x] T33: Rename BCI provider
- [x] T34: Rename CHBMIT provider
- [x] T35: Rename Sleep-EDF provider
- [x] T36: Wire EEGBCI provider
- [x] T37: Wire PhysioNet provider
- [x] T38: Real BIDS conversion
- [x] T39: Real checksum verification
- [x] T40: Real content hash
- [x] T41: Downgrade corpus SRL
- [x] T42: Fix verify CLI
- [x] T43: Fix reproduce CLI
- [x] T44: Delete pipeline runners

## P1-KNOWLEDGE + MODELS
- [x] T45: Wire Knowledge Graph
- [x] T46: Wire Decision Engine
- [x] T47: Real sphere model
- [x] T48: Real BEM model
- [x] T49: Real ADS1299
- [x] T50: Delete hardware stubs
- [x] T51: Delete disease stubs
- [x] T52: Delete hardware twins
- [x] T53: Delete seizure workflow
- [x] T54: Persist failure atlas
- [x] T55: Delete literature verifier
- [x] T56: Delete methodological validator
- [x] T57: Fix incubator

## P1-FRONTEND + DOCS + P2
- [x] T58: Fix frontend build
- [-] T59: FastAPI backend
- [-] T60: Wire frontend to backend
- [x] T61: Real graph queries
- [x] T62: Real evidence service
- [x] T63: Real meta analysis
- [x] T64: Real publication exporter
- [x] T65: Real Bayesian CI
- [x] T66: Reconcile evidence schemas
- [x] T67: Reconcile decision engines
- [x] T68: Reconcile replay files

## P3 + Integration
- [ ] T69: Fix doc claims
- [ ] T70: Doc sync checker
- [ ] T71: KS test synthetic validation
- [ ] T72: Final integration

## Success Criteria
- [ ] S1: Demo produces real evidence
- [ ] S2: No hardcoded CCC in matrix
- [ ] S3: No np.random in native methods
- [ ] S4: Contract violation raisable
- [ ] S5: Transaction hash covers content
- [ ] S6: No hardcoded literature values
- [ ] S7: verify CLI doesn't crash
- [ ] S8: reproduce CLI is honest
- [ ] S9: pytest green
- [ ] S10: No empty algorithm files
- [ ] S11: Frontend either builds or is gone
- [ ] S12: No SRL fraud
- [ ] S13: Doc claims verified
- [ ] S14: Reproducibility hash test passes
- [ ] S15: CSP crossval tests real CSP

## Sprint Status
- Week: 1 of 8
- Tasks completed: 1 / 72
- Tasks blocked: 0
- Success criteria passing: 0 / 15
