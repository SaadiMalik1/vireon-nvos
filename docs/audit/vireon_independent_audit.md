# VIREON — Comprehensive Independent Scientific, Engineering, Documentation, Architecture, and Research-Rigor Audit

**Date:** 2026-08-16
**Commit:** 774d7ed9663c971db39f1e02fd4c5172e63bb046 (v1.0.3 with uncommitted dx/dx2 changes)
**Auditor:** Super Z (GLM-4.6 via Z.ai)
**Method:** Fresh investigation from source code, test execution, dependency behavior

---

## A. Executive Summary

VIREON is a 12-package Python monorepo (30,929 LOC, 1 author, 5-day history) that has evolved from a "Neurotechnology Validation Operating System" concept into a focused validation/evidence layer above MOABB. Its strongest capability is a cryptographically verifiable evidence chain (SHA-256 bundles, tamper detection, partition integrity checking) that has been proven end-to-end with real BCI data (BNCI2014_001, 9 subjects, 83.68% accuracy). Its validation layer can independently discover 5 of 5 tested fault classes from raw execution traces (Study B), including subject/session leakage, below-chance performance, missing reproducibility metadata, and evidence tampering.

**However, VIREON is internally evaluated but independently unvalidated.** No external researcher has used it. No independent publication has reproduced its results. No independent group has evaluated the system. The README claims VIREON "solves the reproducibility crisis" — this is overstated. VIREON provides mechanisms intended to improve computational reproducibility; independent scientific reproduction has not been demonstrated.

The most serious weakness is that VIREON has not yet found a real methodological problem in a published paper. Study C (3 of 5 experiments completed) produced only V1 findings (additional characterization) — 0 V2 findings (potential concerns). The project may be checking a narrow set of generic invariants that are insufficient to generate V2 findings on real research.

**Documentation is significantly drifted.** The API health endpoint reports version 0.4.0 (hardcoded) despite pyproject.toml being 1.2.0. vireon-methods __version__ is 1.0.2. The README claims "Adversarial Digital Twins" which are 33 lines of ABCs. The README claims "22 native algorithms" but 18 of 21 are scipy/sklearn wrappers. ADRs 0001-0007 predate the MOABB pivot and describe an architecture that ADR 0008 has superseded but not formally deprecated.

**Overall research readiness: Research Prototype.** The architecture is sound, the evidence layer works, the fault detection is proven, but the scientific value is unproven and the documentation is not trustworthy.

---

## B. Current Architecture Map

```
VIREON (12 packages, 30,929 LOC)
│
├── vireon-core/ (2,687 LOC) — contracts, kernel, runtime
│   ├── contracts/evidence.py — EvidenceBundle, RegulatoryProfile
│   ├── contracts/plugin.py — ContractValidator, ScientificContractViolation
│   ├── kernel/execution_engine.py — DAG executor, environment fingerprint
│   └── runtime/ — DeterministicRNG, hardware, clock
│
├── vireon-methods/ (4,027 LOC) — 21 algorithm files, 18 are wrappers ← SHOULD DEPRECATE
│   ├── spectral/ (7 files) — Welch, FFT, STFT, Wavelets, Multitaper, Bandpower
│   ├── spatial/ (7 files) — CSP, ICA, FBCSP, xDAWN, Riemannian
│   ├── deep_learning/ (2 files) — EEGNet, DeepConvNet
│   ├── connectivity/ (5 files) — PLV, PLI, wPLI, MI, TransferEntropy
│   └── filtering/ (2 files) — IIR, FIR
│
├── vireon-evidence/ (2,112 LOC) — registry, graph, tamper detection ← CORE
│   ├── registry/core.py — SQLite, INSERT OR IGNORE, get(), search()
│   ├── graph/transactions.py — deterministic hash (sequence_number)
│   └── graph/core.py — NetworkX DAG
│
├── vireon-corpus/ (839 LOC) — 3 datasets, dispatches by key
│   ├── dataset_manager.py — _load_physionet_bci, _load_sleep_edf
│   └── exceptions.py — UnknownDatasetError, DatasetDownloadError
│
├── vireon-knowledge/ (532 LOC) — 20 rules covering 20 methods
│   └── validation_rules/rules.jsonld
│
├── vireon-moabb/ (6,520 LOC) — THE NEW VIREON
│   ├── spec.py — ExperimentSpec
│   ├── executor.py — MoabbExecutor
│   ├── validation.py — ValidationLayer (partition integrity, statistics)
│   ├── evidence.py — EvidenceBundle + verify()
│   ├── report.py — Reporter
│   ├── adapters/ — MOABB, MNE, scipy, sklearn, pyriemann
│   ├── robustness/ — 5 perturbation types
│   ├── statistics/ — subject-level bootstrap, permutation, FDR
│   ├── scorecard.py — 6 dimensions
│   ├── cli.py — validate, inspect, reproduce
│   ├── study_c/ — Study C protocol + C-1 results
│   └── tests/ — 12 tests
│
├── vireon-mcp/ (148 LOC) — 6-tool MCP server (stdio)
├── vireon-validation/ (4,726 LOC) — benchmarks, statistics, regression
├── vireon-verification/ (2,122 LOC) — 32 literature tests (2 collection errors)
├── vireon-models/ (2,092 LOC) — digital twins, hardware ← UNUSED
├── vireon-lab/ (1,318 LOC) — CLI, replay engine
└── vireon-api/ (202 LOC) — FastAPI (auth, CORS, 6 endpoints)
```

**Architecture drift from documentation:**
- README describes "Adversarial Digital Twins" — code is 33 lines of ABCs
- README claims "22 native algorithms" — 18 are wrappers
- ADRs 0001-0007 describe pre-MOABB architecture — ADR 0008 supersedes but doesn't formally deprecate
- API health endpoint reports 0.4.0 — actual version is 1.2.0

---

## C. Documentation Drift Report

| Document | Claim | Current reality | Status | Required correction |
|----------|-------|-----------------|--------|-------------------|
| README.md | "Adversarial Digital Twins" | 33 lines of ABCs in vireon-models | OVERSTATED | Remove or qualify |
| README.md | "22 native algorithms" | 18 of 21 are scipy/sklearn wrappers | OVERSTATED | Change to "delegates to scipy/MNE/sklearn" |
| README.md | "solves the reproducibility crisis" | No independent researcher has used VIREON | OVERSTATED | Change to "provides mechanisms intended to improve reproducibility" |
| API health | version="0.4.0" | pyproject.toml says 1.2.0 | FALSE | Fix main.py:74 |
| vireon-methods __init__ | __version__="1.0.2" | pyproject.toml says 1.2.0 | OUTDATED | Sync to 1.2.0 |
| ADRs 0001-0007 | "Validation Not Simulation" architecture | ADR 0008 supersedes with MOABB integration | PARTIALLY CURRENT | Add "Superseded by ADR 0008" to 0001-0007 |
| CHANGELOG | Stops at v1.0.0 (original) | v1.2.0 entry added | PARTIALLY ACCURATE | Missing v1.0.1, v1.0.2, v1.0.3 entries |
| .gitignore | Has *.db rule | 2 .db files still tracked | INCONSISTENT | git rm --cached |
| Study C protocol | "5 experiments across 3 paradigms" | 3 completed (all motor imagery), 2 fixed but not run | OVERSTATED | State "3 completed, 2 pending" |

---

## D. ADR Audit Report

| ADR | Decision | Current implementation | Status | Evidence | Recommended action |
|-----|----------|------------------------|--------|----------|-------------------|
| 0001 | Validation not simulation | MOABB integration delegates execution | SUPERSEDED by 0008 | ADR 0008 refines it | Mark as "Refined by ADR 0008" |
| 0002 | Plugin-first kernel | Plugin system exists but is unused in vireon-moabb | PARTIALLY CURRENT | vireon-methods still uses IPlugin | Evaluate whether plugin system is still needed |
| 0003 | Scientific contracts | ContractValidator exists, runs ADF test | CURRENT | plugin.py:103-125 | KEEP |
| 0004 | Evidence engine | EvidenceBundle + Registry + Graph | CURRENT | All verified working | KEEP |
| 0005 | Knowledge graph | 20 rules, AST evaluator | CURRENT | rules.jsonld has 20 rules | KEEP |
| 0006 | SRL model | Not implemented in code | UNIMPLEMENTED | No SRL code found | Create ADR or remove |
| 0007 | Source space architecture | vireon-models exists but unused | OBSOLETE | 2,092 LOC, zero callers | Deprecate |
| 0008 | MOABB integration | vireon-moabb package built, POC proven | CURRENT | 6,520 LOC, real evidence | KEEP |

---

## E. Scientific Validity Report

### Algorithmic correctness
- FBCSP: FIXED ✓ (applies band-pass per band)
- EEGNet: FIXED ✓ (BatchNorm, ELU, AvgPool, Dropout — matches Lawhern 2018)
- DeepConvNet: FIXED ✓ (4 conv blocks, AdaptiveAvgPool — matches Schirrmeister 2017)
- MI: FIXED ✓ (real Kraskov k-NN via cKDTree)
- **BUT**: 18/21 files are wrappers — VIREON should not claim "native implementations"

### Experimental correctness
- Partition integrity: ✓ (checks actual train/test subject/session overlap)
- CrossSession semantics: ✓ (same subject in train/test is valid, different sessions)
- CrossSubject semantics: ✓ (strict subject isolation enforced)
- Subject-level statistics: ✓ (bootstrap over subjects, not trials — avoids pseudoreplication)

### Statistical correctness
- Subject-level bootstrap CI: ✓ (resamples 9 subjects, not 2592 trials)
- Permutation test: ✓ (subject-level, p=0.002 for CSP+LDA)
- Pseudoreplication detection: ✓ (CI width analysis catches trial-level bootstrap)
- **GAP**: No multiple-comparison correction in the standard pipeline (FDR exists but not wired)

### Evidence validity
- SHA-256 hashing: ✓ (integrity)
- Tamper detection: ✓ (INSERT OR IGNORE, EvidenceAlreadyRegisteredError)
- EvidenceBundle.verify(): ✓ (returns False when content modified)
- **BUT**: Hash proves integrity, not validity. A hash of a wrong result is still a valid hash.

### Reproducibility
- DeterministicRNG: ✓ (PCG64, seed=42)
- PyTorch determinism: ✓ (manual_seed, cudnn.deterministic)
- Transaction hash: ✓ (sequence_number, not wall-clock)
- BLAS threads: ✗ NOT PINNED (threadpoolctl not used)
- Cross-machine: UNVERIFIED (only tested on one machine)
- Git commit in evidence bundle: ✗ NOT CAPTURED

### External validation
**STATUS: NONE**
- No external researcher has used VIREON
- No independent publication has reproduced results
- No independent group has evaluated the system
- **Classification: internally evaluated but independently unvalidated**

---

## F. Test and Validation Report

### Test inventory (OBSERVED)

| Package | Passed | Failed | Errors | Skipped |
|---------|--------|--------|--------|---------|
| vireon-core | 39 | 0 | 0 | 0 |
| vireon-methods | 60 | 0 | 0 | 0 |
| vireon-evidence | 28 | 1 | 0 | 0 |
| vireon-corpus | 5 | 1 | 0 | 0 |
| vireon-knowledge | 4 | 0 | 0 | 0 |
| vireon-moabb | 11 | 0 | 0 | 1 |
| vireon-validation | 95 | 1 | 0 | 1 |
| literature | — | — | 2 | — |
| **Total** | **~242** | **3** | **2** | **2** |

### Failed tests
1. `test_transaction_hash.py::test_same_bundle_same_hash` — regression from deterministic hash fix
2. `test_bids_conversion.py::test_convert_to_bids_structure` — BIDS conversion failure
3. `test_permutation.py::test_cluster_based_permutation_test` — timeout (performance)

### Collection errors
1. `test_lawhern_2018.py` — NameError
2. `test_schirrmeister_2017.py` — NameError

### Test quality assessment
- vireon-moabb tests: REAL — verify FBCSP filtering, EEGNet architecture, MI Kraskov, registry tamper detection, dataset dispatch, transaction hash determinism. These are meaningful scientific tests.
- vireon-methods tests: Real cross-validation against scipy/MNE at 1e-7 tolerance.
- Literature tests: 2 collection errors (NameError) — these tests cannot even be collected, let alone run.
- **Does the test suite provide evidence of scientific correctness?** Partially. The dx tests verify the fixes are real. But the collection errors and regression indicate infrastructure issues.

### Study B results
5/5 fault classes detected from raw execution trace. This is the strongest evidence of validation capability.

### Study C results
3/5 completed. All V1 (additional characterization). 0 V2 (concerns). This means VIREON has not yet found a real methodological problem.

---

## G. Claims Audit

| Claim | Source | Evidence grade | Risk of overclaiming | Correction |
|-------|--------|---------------|---------------------|------------|
| "Solves the reproducibility crisis" | README | E1 (code exists) | CRITICAL | Change to "provides mechanisms intended to improve reproducibility" |
| "22 native algorithms" | README | E1 (code exists) | HIGH | 18/21 are wrappers; change to "delegates to scipy/MNE/sklearn" |
| "Adversarial Digital Twins" | README | E1 (code exists) | HIGH | 33 lines of ABCs; remove or qualify as "planned" |
| "Cryptographic evidence bundles" | README | E4 (end-to-end validated) | LOW | Accurate — SHA-256 verified |
| "Tamper detection" | README | E4 (end-to-end validated) | LOW | Accurate — EvidenceAlreadyRegisteredError fires |
| "Subject-level statistics" | ADR 0008 | E4 (end-to-end validated) | LOW | Accurate — bootstrap over subjects |
| "Partition integrity" | Study B | E4 (end-to-end validated) | LOW | Accurate — detects subject/session overlap |
| "Research-ready" | Implied by v1.0.3 tag | E2 (tests pass) | CRITICAL | Not independently validated |
| "Production/Stable" | pyproject.toml classifier | E1 (code exists) | HIGH | Change to "Development Status :: 4 - Beta" |
| "Validated by tests" | Implied | E2 (tests pass) | HIGH | Tests prove software correctness, not scientific validity |

---

## H. Risk Register

| ID | Finding | Category | Severity | Evidence | Impact | Recommended action |
|----|---------|----------|----------|----------|--------|-------------------|
| R01 | No independent researcher has used VIREON | VALIDATION GAP | CRITICAL | No external publications, no external users | Cannot claim research validation | Execute Study C with independent adjudication |
| R02 | 0 V2 findings in Study C (3/5 completed) | VALIDATION GAP | HIGH | C-1/C-2/C-3 all V1 | VIREON may be too conservative to detect real problems | Complete C-4/C-5 and adjudicate |
| R03 | API health reports version 0.4.0 | DOCUMENTATION DEFECT | MEDIUM | main.py:74 | Users see wrong version | Fix to 1.2.0 |
| R04 | 2 .db files committed to git | SECURITY DEFECT | MEDIUM | git ls-files shows .db | Binary state in git, integrity concern | git rm --cached |
| R05 | 2 literature test collection errors | SOFTWARE BUG | MEDIUM | NameError in test files | Cannot verify literature reproductions | Fix import errors |
| R06 | 18/21 algorithm files are wrappers | ARCHITECTURAL DEFECT | MEDIUM | grep shows scipy/sklearn imports | Maintenance burden, duplication | Deprecate to reference/deprecated/ |
| R07 | BLAS threads not pinned | REPRODUCIBILITY DEFECT | MEDIUM | No threadpoolctl usage | Cross-machine hash instability | Add pinned_blas_threads context manager |
| R08 | README claims "solves reproducibility crisis" | CLAIM/COMMUNICATION PROBLEM | HIGH | README.md | Overstated claim | Rewrite to "provides mechanisms intended to improve reproducibility" |
| R09 | vireon-models unused (2,092 LOC) | ARCHITECTURAL DEFECT | LOW | Zero callers | Dead code | Remove or deprecate |
| R10 | ADRs 0001-0007 not formally superseded | GOVERNANCE/ADR DEFECT | LOW | No "Superseded" marker | Architectural confusion | Add "Refined by ADR 0008" to 0001-0007 |
| R11 | MassiveCampaignOrchestrator is stub | SOFTWARE BUG | LOW | Empty loop body | Misleading if users call it | Remove or implement |
| R12 | Transaction hash test regression | SOFTWARE BUG | MEDIUM | test_same_bundle_same_hash fails | Test suite not clean | Fix test to match new deterministic hash |
| R13 | Git commit not captured in evidence bundle | REPRODUCIBILITY DEFECT | MEDIUM | No git rev-parse in bundle | Cannot trace evidence to code version | Add git commit hash to environment fingerprint |
| R14 | vireon-methods __version__ = 1.0.2 | DOCUMENTATION DEFECT | LOW | Not synced to 1.2.0 | Version confusion | Sync to 1.2.0 |

---

## I. Research-Readiness Verdict

### Classification: 3. Research Prototype

**Justification:**

VIREON has a working end-to-end pipeline (ExperimentSpec → MOABB → ValidationLayer → EvidenceBundle → Report) that has been demonstrated with real BCI data. Its evidence layer is production-capable (SHA-256, tamper detection, INSERT OR IGNORE, deterministic hashes). Its validation layer can independently discover 5/5 tested fault classes from raw execution traces (Study B).

**However, it is NOT Research-Ready (4) because:**
1. No independent researcher has used it (Level 5 reproducibility not achieved)
2. Study C has not produced any V2 findings (VIREON has not yet found a real problem)
3. Documentation is significantly drifted (API version, README claims, ADR status)
4. Test suite has 3 failures and 2 collection errors
5. 18/21 algorithm files are wrappers that should be deprecated
6. BLAS threads not pinned, git commit not captured in evidence

**It is NOT merely an Engineering Prototype (2) because:**
1. The evidence layer is production-capable (A-grade)
2. Study B proves the validation layer can discover faults from raw data
3. The MOABB integration is architecturally sound and proven with real data
4. Study C protocol is preregistered and scientifically rigorous

---

## J. What Would an Independent Researcher Experience?

A researcher cloning the repository tomorrow would:

1. **Clone and install:** Follow README instructions. `pip install -e .` would work. They would see 10 packages plus the new vireon-moabb and vireon-mcp.

2. **Read the README:** See claims about "Adversarial Digital Twins," "22 native algorithms," and "solving the reproducibility crisis." They would be impressed but confused when they discover that digital twins are 33 lines of ABCs, 18/21 algorithms are wrappers, and no independent validation exists.

3. **Try the CLI:** Run `vireon validate BNCI2014_001` — this might work if MOABB is installed and data is downloaded, but they would need to discover that the CLI is in `vireon_moabb.cli`, not `vireon_lab.cli`. The README doesn't mention vireon-moabb.

4. **Check the API:** Start the FastAPI server (if they figure out the Dockerfile runs uvicorn). The health endpoint would report version 0.4.0. They would see auth and CORS configured but wouldn't know to set VIREON_API_KEY.

5. **Examine evidence:** Find the POC evidence bundle (hash 17d03af8...) and verify it. This would work — EvidenceBundle.verify() returns True. They would be impressed by the cryptographic provenance.

6. **Run Study C:** Find the protocol, try to run experiments. C-1 would work (data cached). C-4 and C-5 would require downloading EPFLP300 and Wang2016 data. They might encounter timeout issues.

7. **Read the ADRs:** See 8 ADRs. ADRs 0001-0007 describe a pre-MOABB architecture. ADR 0008 describes the MOABB integration. They would be confused about which architecture is current.

8. **Examine the validation layer:** Discover that VIREON checks partition integrity, subject-level statistics, robustness, and evidence integrity. They would be impressed by Study B (5/5 faults detected). They would be concerned that Study C produced 0 V2 findings.

9. **Try to adjudicate:** Find the adjudication form template. Realize they need to be the independent adjudicator but they're also the person running the experiments. This is a conflict of interest.

10. **Overall experience:** Impressed by the evidence layer and fault detection capability. Confused by documentation drift. Frustrated by the gap between claims and reality. Uncertain whether VIREON actually adds scientific value beyond benchmarking.

---

## 27. Final Reviewer Question

> **If a skeptical neurotechnology researcher encountered VIREON for the first time today, what could they safely trust, what could they not yet trust, and what evidence would be required to move VIREON to the next level of scientific credibility?**

### What they could safely trust:
- The SHA-256 evidence bundles are cryptographically sound (verified by execution)
- The tamper detection works (EvidenceAlreadyRegisteredError fires on content mismatch)
- The partition integrity checks inspect actual train/test membership (not just evaluation class names)
- The subject-level statistics avoid pseudoreplication (bootstrap over 9 subjects, not 2592 trials)
- The MOABB integration works end-to-end (proven with real BNCI2014_001 data at 83.68% accuracy)
- Study B demonstrates 5/5 fault detection from raw execution traces

### What they could not yet trust:
- That VIREON can find real methodological problems in published papers (Study C: 0 V2 findings in 3 experiments)
- That VIREON is reproducible across machines (BLAS not pinned, cross-machine unverified)
- That the README claims are accurate ("solves the reproducibility crisis," "22 native algorithms," "Adversarial Digital Twins")
- That the evidence bundle captures all necessary provenance (git commit not captured, BLAS not pinned)
- That the scorecard is scientifically validated (weights are heuristic, no empirical justification)
- That the MCP server works with real AI clients (untested with Claude Desktop/Cursor)
- That the regulatory binder generates valid submissions (still a stub)

### Evidence required to move VIREON to the next level:
1. **At least one V3 finding** (VIREON detects a real methodological problem, independently confirmed by an adjudicator who didn't build VIREON)
2. **Cross-machine reproduction** (same spec + seed on two different machines → same SHA-256 hash)
3. **External researcher usage** (at least one researcher who is not the author successfully uses VIREON and publishes results)
4. **Documentation accuracy** (README, API health, ADR status, version strings all match implementation)
5. **Deprecation of redundant code** (18 wrapper algorithm files moved to deprecated/)
6. **Peer review** (the Study C protocol and results submitted to a venue like Journal of Neural Engineering or NeuroImage)

Until these are achieved, VIREON is a promising research prototype with a working evidence layer and demonstrated fault-detection capability, but it is not yet a validated research instrument.
