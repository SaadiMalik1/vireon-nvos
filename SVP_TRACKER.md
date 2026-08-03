# VIREON SVP Milestone Tracker

## Status Legend
- [ ] Not started
- [~] In progress
- [x] Done
- [!] Blocked

## Workstream A — Algorithm Validation Suite
- [x] S01: FFT validation suite
- [x] S02: STFT + wavelet validation
- [x] S03: FIR + IIR filter validation
- [x] S04: ICA + CSP validation
- [x] S05: Beamforming + source localization validation
- [x] S06: Connectivity validation
- [x] S07: Algorithm validation report (PDF)
- [x] S08: CI algorithm regression gate

## Workstream B — Literature Reproduction
- [x] S09: Welch 1967
- [x] S10: Ramoser 2000 (CSP)
- [x] S11: Hyvärinen & Oja 2000 (FastICA)
- [x] S12: Vinck 2011 (wPLI)
- [x] S13: Literature reproduction report

## Workstream C — Statistical Rigor
- [ ] S14: Bootstrap CIs
- [ ] S15: Permutation testing
- [ ] S16: Effect sizes
- [ ] S17: Multiple comparison correction (FDR)
- [ ] S18: Statistical rigor integration test

## Workstream D — Evidence Infrastructure
- [ ] S19: SQLite-persistent evidence graph
- [ ] S20: Evidence registry
- [ ] S21: DOI minting
- [ ] S22: Complex graph queries
- [ ] S23: Evidence export formats (JSON-LD, RDF, BibTeX)

## Workstream E — Publication Pipeline + API + Docs
- [ ] S24: LaTeX paper generator
- [ ] S25: Jupyter notebook generator
- [ ] S26: FastAPI backend
- [ ] S27: HTML dashboard
- [ ] S28: Tutorial suite
- [ ] S29: API reference generator
- [ ] S30: Final integration + tag v0.4.0

## Success Criteria
- [x] V1: All 11 native algorithms validated against reference with declared tolerances (0 regressions)
- [x] V2: ≥4 canonical literature reproductions pass with evidence bundles (Welch 1967, Ramoser 2000, Hyvärinen 2000, Vinck 2011)
- [ ] V3-V15 (see playbook §2)

## Milestone Status
- Week: 3 of 6
- Tasks completed: 13 / 30
- Success criteria passing: 2 / 15
