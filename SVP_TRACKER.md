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
- [x] S14: Bootstrap CIs
- [x] S15: Permutation testing
- [x] S16: Effect sizes
- [x] S17: Multiple comparison correction (FDR)
- [x] S18: Statistical rigor integration test

## Workstream D — Evidence Infrastructure
- [x] S19: SQLite-persistent evidence graph
- [x] S20: Evidence registry
- [x] S21: DOI minting
- [x] S22: Complex graph queries
- [x] S23: Evidence export formats (JSON-LD, RDF, BibTeX)

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
- [x] V3: Bootstrap CIs, permutation tests, effect sizes, and FDR correction integrated (S14-S18)
- [x] V4: SQLite-persistent evidence graph, registry, DOI minting, and multi-format exports working (S19-S23)
- [ ] V5-V15 (see playbook §2)

## Milestone Status
- Week: 5 of 6
- Tasks completed: 23 / 30
- Success criteria passing: 4 / 15
