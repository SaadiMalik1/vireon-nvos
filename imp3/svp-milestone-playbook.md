# VIREON Scientific Validation Platform Milestone — From Research Prototype to Outstanding

**Target:** `github.com/SaadiMalik1/vireon-nvos` (current: Research Prototype, post-integration)
**Scope:** 27 tasks (S01-S27) across 5 workstreams
**Duration:** 6 weeks (42 days)
**Cadence:** 4-5 tasks/week
**Maintainer role:** Review each PR before merge; no autonomous merge

---

## 0. Read This First

VIREON has reached **Research Prototype** status: the evidence pipeline works end-to-end, 246 tests pass, the demo produces real cryptographic evidence, and multi-subject validation with meta-analysis is functional. The native algorithm library is world-class (Welch, FFT, STFT, wavelets, ICA, CSP, FIR, IIR, beamforming, source localization, connectivity — all matching scipy/MNE to machine precision).

This milestone pushes VIREON from **Research Prototype** to **Scientific Validation Platform** — a system that can be used by external researchers to validate their own algorithms, reproduce published results, and generate publication-ready evidence.

The defining question: **Can an external researcher install VIREON, validate their algorithm against 5+ reference implementations, reproduce 4+ published papers, and generate a publication-ready evidence report?**

If yes → VIREON is a Scientific Validation Platform.
If no → VIREON remains a research prototype with excellent components.

---

## 1. Goal

Convert VIREON from **Research Prototype** to **Scientific Validation Platform** by the end of week 6.

A Scientific Validation Platform, for this milestone's purposes, means:

1. **Every native algorithm is benchmarked** against its reference (scipy/MNE/sklearn) with a formal validation report showing numerical agreement, edge cases, and performance characteristics.
2. **Four canonical papers are reproduced** from the literature, with real datasets, real pipelines, and evidence bundles proving the reproduction.
3. **Statistical rigor is enforced** — every metric has confidence intervals (bootstrap), every comparison has effect sizes, every multiple comparison has FDR correction.
4. **Evidence is persistent and queryable** — the evidence graph survives process restarts (SQLite), supports complex queries, and can be exported for external review.
5. **Publication-ready outputs** — VIREON generates LaTeX papers, Jupyter notebooks, and interactive HTML dashboards from evidence bundles.
6. **A REST API** allows external tools to query evidence, trigger benchmarks, and retrieve reports.
7. **Documentation is comprehensive** — tutorials, API reference, scientific manual, reproducibility handbook — all verified against code.

---

## 2. Success Criteria (Minimum Bar)

The milestone is a **success** if and only if ALL of the following are true at the end of week 6:

| # | Criterion | Verification Command | Pass Condition |
|---|---|---|---|
| V1 | All 11 native algorithms benchmarked | `pytest tests/test_algorithm_validation_suite.py -v` | 11 algorithms pass numerical cross-validation |
| V2 | Algorithm validation report generated | `ls reports/algorithm_validation_report.pdf` | File exists, > 20 pages, covers all 11 algorithms |
| V3 | 4 literature papers reproduced | `pytest vireon-verification/literature/ -v` | ≥ 4 PASSED (not SKIPPED) |
| V4 | Bootstrap CI on every metric | `rg "bootstrap_ci\|compute_bootstrap" vireon-validation/` | ≥ 5 matches in production code |
| V5 | Permutation tests available | `rg "permutation_test" vireon-validation/` | ≥ 2 matches |
| V6 | FDR correction implemented | `rg "fdr_correction\|benjamini" vireon-validation/` | ≥ 1 match |
| V7 | Evidence graph persists to SQLite | `python -c "from vireon_evidence.graph.core import EvidenceGraph; g=EvidenceGraph(db_path=':memory:'); g.persist(); g2=EvidenceGraph(db_path=':memory:'); assert len(g2.list_nodes()) > 0"` | Nodes survive restart |
| V8 | LaTeX paper generator works | `python -c "from vireon_evidence.exporters.latex_generator import LaTeXReportGenerator; r=LaTeXReportGenerator(bundle); tex=r.generate(); assert '\\\\documentclass' in tex"` | Valid LaTeX output |
| V9 | Jupyter notebook generator works | `python -c "from vireon_evidence.exporters.notebook_generator import NotebookGenerator; nb=NotebookGenerator(bundle).generate(); assert 'cells' in nb"` | Valid notebook dict |
| V10 | FastAPI backend serves evidence | `curl localhost:8000/api/evidence` | Returns JSON list |
| V11 | REST API triggers benchmark | `curl -X POST localhost:8000/api/benchmark -d '{"algorithm":"csp","dataset":"physionet_s1"}'` | Returns bundle hash |
| V12 | Tutorials exist and are accurate | `ls docs/tutorials/*.md` | ≥ 4 tutorial files |
| V13 | API reference auto-generated | `python scripts/generate_api_reference.py && ls docs/api_reference.md` | File exists, > 500 lines |
| V14 | Full test suite passes | `pytest --tb=no -q` | 0 failures, 0 collection errors |
| V15 | Coverage > 75% on new code | `pytest --cov=vireon-validation --cov=vireon-evidence --cov-fail-under=75` | Passes |

---

## 3. The 6-Week Plan

### Week 1-2: Workstream A — Algorithm Validation Suite (S01-S06)

Benchmark every native algorithm against its reference. This is the core scientific value.

| Day | Task | Effort |
|---|---|---|
| 1 | S01: FFT validation suite (vs scipy.fft, scipy.periodogram) | M |
| 2 | S02: STFT + wavelet validation suite (vs scipy.signal.stft, scipy.signal.cwt) | M |
| 3 | S03: FIR + IIR filter validation (vs scipy.signal.firwin, scipy.signal.butter) | M |
| 4 | S04: ICA + CSP validation suite (vs sklearn FastICA, mne.decoding.CSP) | M |
| 5 | S05: Beamforming + source localization validation (vs mne.beamformer, mne.minimum_norm) | L |
| 6 | S06: Connectivity validation suite (coherence, PLV, PLI, wPLI, AEC vs mne.connectivity) | L |
| 7-8 | S07: Generate algorithm validation report (PDF, > 20 pages, all 11 algorithms) | M |
| 9-10 | S08: Add algorithm validation to CI — regression test for numerical agreement | S |

**End of week 2 gate:** V1, V2, V8 (partial — report exists) pass.

### Week 3: Workstream B — Literature Reproduction (S09-S12)

Reproduce 4 canonical papers with real datasets.

| Day | Task | Effort |
|---|---|---|
| 11 | S09: Reproduce Welch 1967 (PSD estimation) — DOI: 10.1109/TAU.1967.1161901 | M |
| 12 | S10: Reproduce Ramoser 2000 (CSP for BCI) — DOI: 10.1109/86.84781 | M |
| 13 | S11: Reproduce Hyvärinen & Oja 2000 (FastICA) — DOI: 10.1016/S0893-6080(00)00026-5 | M |
| 14 | S12: Reproduce Vinck 2011 (wPLI) — DOI: 10.1016/j.neuroimage.2011.01.055 | M |
| 15 | S13: Literature reproduction report — formal document linking each paper to its evidence bundle | S |

**End of week 3 gate:** V3 passes (4 literature tests PASSED, not SKIPPED).

### Week 4: Workstream C — Statistical Rigor (S14-S17)

Every metric has uncertainty quantification.

| Day | Task | Effort |
|---|---|---|
| 16 | S14: Bootstrap confidence intervals for all metrics (CCC, RMSE, accuracy, kappa) | M |
| 17 | S15: Permutation testing framework (cluster-based, max-stat, FDR) | M |
| 18 | S16: Effect size computation (Cohen's d, Hedges' g, η², partial η²) | S |
| 19 | S17: Multiple comparison correction (Bonferroni, FDR-BH, permutation-based) | S |
| 20 | S18: Statistical rigor integration test — every evidence bundle has CIs | S |

**End of week 4 gate:** V4, V5, V6 pass.

### Week 5: Workstream D — Evidence Infrastructure (S19-S22)

Persistent, queryable, exportable evidence.

| Day | Task | Effort |
|---|---|---|
| 21 | S19: SQLite-persistent evidence graph (survives process restart) | M |
| 22 | S20: Evidence registry — export/import bundles, provenance tracking | M |
| 23 | S21: DOI minting for evidence bundles (via Zenodo API or local mock) | M |
| 24 | S22: Complex graph queries — "show me all methods validated on PhysioNet with CCC > 0.8" | M |
| 25 | S23: Evidence export to external formats (JSON-LD, RDF, BibTeX) | S |

**End of week 5 gate:** V7 passes.

### Week 6: Workstream E — Publication Pipeline + API + Docs (S24-S27)

| Day | Task | Effort |
|---|---|---|
| 26 | S24: LaTeX paper generator from evidence bundles | M |
| 27 | S25: Jupyter notebook generator (executable reproduction) | M |
| 28 | S26: FastAPI backend (REST API for evidence, benchmarks, queries) | L |
| 29 | S27: Interactive HTML dashboard (evidence browser, leaderboard, timeline) | M |
| 30 | S28: Tutorial suite (4+ tutorials: quickstart, algorithm validation, literature reproduction, evidence graph) | M |
| 31 | S29: Auto-generated API reference (mkdocstrings) | S |
| 32-33 | S30: Final integration — verify V1-V15, tag v0.4.0-scientific-validation-platform | M |
| 34-42 | Buffer for rework + polish | — |

**End of week 6 gate:** V1-V15 all pass. Tag `v0.4.0-scientific-validation-platform`.

---

## 4. Agent Operating Rules

### R1: One task per session
The agent works on exactly one task ID at a time. No batching. No looking ahead.

### R2: Test-first (TDD)
For every new feature, write the test before the implementation. Red → green → refactor.

### R3: No new np.random
All randomness via `DeterministicRNG`. This is now enforced by CI grep gates.

### R4: No hardcoded scientific constants
Every metric computed from data or declared as a named constant with a source comment.

### R5: No fake file artifacts
No literal strings as binary files. If a library is unavailable, raise an honest error.

### R6: No fabricated metrics
Every number computed from real data. No `int(total * 0.05)`, no hardcoded CCC.

### R7: One PR per task
Branch `svp/S<NN>-<slug>`, commit, PR, wait for review.

### R8: Verification before claiming done
Run every verification command. Paste output in PR.

### R9: Preserve the honest core
The 21 honest-core files from the previous playbook are off-limits to breakage.

### R10: Document every public API change
Update docs in the same PR if you change a public API.

### R11: Numerical cross-validation for all algorithms
Every algorithm must be tested against a reference (scipy/MNE/sklearn) with a declared tolerance. Tests must fail if the algorithm deviates.

### R12: Statistical rigor
Every reported metric must include a confidence interval (bootstrap) and effect size. No bare point estimates.

### R13: Evidence persistence
Every evidence bundle must be persistable to SQLite and exportable to JSON-LD.

### R14: Publication-ready
Every evidence bundle must be convertible to LaTeX, Jupyter notebook, and HTML dashboard.

### R15: If blocked, escalate
3 failures → write `BLOCKED.md`, stop, wait for maintainer.

---

## 5. Verification Gates

### G1: pytest green (no --ignore)
```bash
pytest --tb=short -q
```

### G2: Algorithm validation suite
```bash
pytest tests/test_algorithm_validation_suite.py -v
```
All 11 algorithms pass numerical cross-validation against references.

### G3: Literature reproduction
```bash
pytest vireon-verification/literature/ -v
```
≥ 4 tests PASSED (not SKIPPED).

### G4: Statistical rigor
```bash
pytest tests/test_statistical_rigor.py -v
```
Bootstrap CIs, permutation tests, FDR correction all verified.

### G5: Evidence persistence
```bash
python -c "
from vireon_evidence.graph.core import EvidenceGraph
g = EvidenceGraph(db_path='/tmp/test_evidence.db')
# Add nodes, persist, reload
g.persist()
g2 = EvidenceGraph(db_path='/tmp/test_evidence.db')
assert len(g2.list_nodes()) == len(g.list_nodes())
"
```

### G6: Publication outputs
```bash
python -c "
from vireon_evidence.exporters.latex_generator import LaTeXReportGenerator
from vireon_evidence.exporters.notebook_generator import NotebookGenerator
# Load a real bundle, generate outputs
tex = LaTeXReportGenerator(bundle).generate()
assert '\\documentclass' in tex
nb = NotebookGenerator(bundle).generate()
assert 'cells' in nb
"
```

### G7: REST API
```bash
# Start server in background
uvicorn vireon_api.main:app --port 8000 &
sleep 2
curl -s localhost:8000/api/evidence | python -m json.tool
curl -s -X POST localhost:8000/api/benchmark -d '{"algorithm":"csp","dataset":"physionet_s1"}'
kill %1
```

### G8: Human review checkpoint
Maintainer reviews each PR. For algorithm validation tasks, maintainer verifies the numerical tolerance is appropriate. For literature reproduction, maintainer verifies the pipeline matches the paper's methodology.

---

## 6. Definition of Done

A task is **Done** when:
1. All acceptance criteria in the prompt are met.
2. All verification commands pass (output pasted in PR).
3. Maintainer has approved and merged.
4. No new violations of R3-R6 introduced.
5. Task marked complete in `SVP_TRACKER.md`.

The **milestone** is Done when V1-V15 all pass and the release is tagged `v0.4.0-scientific-validation-platform`.

---

## 7. Forbidden Patterns (Auto-Reject)

| Pattern | Why forbidden | Detection |
|---|---|---|
| `np.random.*` without DeterministicRNG | Breaks reproducibility | `rg "np\.random\.(normal\|uniform\|choice)"` |
| `return 0.94` / `return 0.95` | Hardcoded metrics | `rg "return 0\.\d+"` |
| `# Stub` / `# Stubbed` | Silent stubs | `rg "# [Ss]tub"` |
| `evidence_hash = ""` | Empty hash | `rg 'evidence_hash.*=.*""'` |
| `PARQUET_STUB_DATA` | Fake file | `rg "STUB_DATA"` |
| `int(total_runs * 0.05)` | Fabricated count | `rg "int\(total_runs \* 0\.05\)"` |
| Bare point estimate without CI | No uncertainty | Review in PR |
| `@pytest.mark.skip` without reason | Silent skip | `rg "pytest\.mark\.skip\(\s*\)"` |
| Algorithm test without reference comparison | Not validated | Review in PR |

---

## 8. Risk Register

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Algorithm validation reveals numerical disagreement with reference | Medium | High | Document the disagreement honestly. If Vireon's implementation is correct but differs from reference (e.g., different normalization), document the choice. If Vireon is wrong, fix it. |
| Literature reproduction requires datasets that need ethical approval | Low | Medium | Use only open datasets (PhysioNet, Sleep-EDF, ERP CORE). Never require restricted data. |
| SQLite evidence graph is too slow for large graphs | Low | Medium | Start with SQLite; if > 10k nodes, add PostgreSQL backend later. |
| LaTeX generator requires LaTeX installation | Medium | Low | Generate .tex file (no compilation required). User compiles locally. |
| FastAPI backend adds security surface | Low | Medium | No authentication in v0.4 (local-only). Document clearly. Add auth in v0.5. |
| Coverage gate (75%) is too strict | Low | Low | If legitimate code can't be tested (e.g., GPU paths), add `# pragma: no cover` with comment. |

---

## 9. Task Dependency Graph

```
S01-S06 (algorithm validation) ──> S07 (validation report) ──> S08 (CI regression)
S01-S06 ──> S09-S12 (literature reproduction — needs validated algorithms)
S14-S17 (statistical rigor) ──> S18 (integration test)
S19 (SQLite persistence) ──> S20 (registry) ──> S21 (DOI minting)
S19 ──> S22 (complex queries)
S24 (LaTeX) ──> S27 (HTML dashboard)
S25 (Jupyter) — independent
S26 (FastAPI) ──> S27 (HTML dashboard consumes API)
S28 (tutorials) — depends on everything
S29 (API reference) — independent
ALL ──> S30 (final integration)
```

**Critical path:** S01-S06 → S07 → S09-S12 → S30. If any task on this path slips, the milestone slips.

---

## 10. Prompt Index

All 30 prompts live in `/svp-prompts/`. Naming: `S<NN>-<slug>.md`.

### Workstream A — Algorithm Validation Suite (S01-S08)
- [S01-fft-validation-suite.md](svp-prompts/S01-fft-validation-suite.md)
- [S02-stft-wavelet-validation.md](svp-prompts/S02-stft-wavelet-validation.md)
- [S03-filter-validation.md](svp-prompts/S03-filter-validation.md)
- [S04-ica-csp-validation.md](svp-prompts/S04-ica-csp-validation.md)
- [S05-beamforming-source-validation.md](svp-prompts/S05-beamforming-source-validation.md)
- [S06-connectivity-validation.md](svp-prompts/S06-connectivity-validation.md)
- [S07-algorithm-validation-report.md](svp-prompts/S07-algorithm-validation-report.md)
- [S08-ci-algorithm-regression.md](svp-prompts/S08-ci-algorithm-regression.md)

### Workstream B — Literature Reproduction (S09-S13)
- [S09-reproduce-welch-1967.md](svp-prompts/S09-reproduce-welch-1967.md)
- [S10-reproduce-ramoser-2000.md](svp-prompts/S10-reproduce-ramoser-2000.md)
- [S11-reproduce-hyvarinen-2000.md](svp-prompts/S11-reproduce-hyvarinen-2000.md)
- [S12-reproduce-vinck-2011.md](svp-prompts/S12-reproduce-vinck-2011.md)
- [S13-literature-reproduction-report.md](svp-prompts/S13-literature-reproduction-report.md)

### Workstream C — Statistical Rigor (S14-S18)
- [S14-bootstrap-confidence-intervals.md](svp-prompts/S14-bootstrap-confidence-intervals.md)
- [S15-permutation-testing.md](svp-prompts/S15-permutation-testing.md)
- [S16-effect-sizes.md](svp-prompts/S16-effect-sizes.md)
- [S17-multiple-comparison-correction.md](svp-prompts/S17-multiple-comparison-correction.md)
- [S18-statistical-rigor-integration.md](svp-prompts/S18-statistical-rigor-integration.md)

### Workstream D — Evidence Infrastructure (S19-S23)
- [S19-sqlite-evidence-graph.md](svp-prompts/S19-sqlite-evidence-graph.md)
- [S20-evidence-registry.md](svp-prompts/S20-evidence-registry.md)
- [S21-doi-minting.md](svp-prompts/S21-doi-minting.md)
- [S22-complex-graph-queries.md](svp-prompts/S22-complex-graph-queries.md)
- [S23-evidence-export-formats.md](svp-prompts/S23-evidence-export-formats.md)

### Workstream E — Publication Pipeline + API + Docs (S24-S30)
- [S24-latex-paper-generator.md](svp-prompts/S24-latex-paper-generator.md)
- [S25-jupyter-notebook-generator.md](svp-prompts/S25-jupyter-notebook-generator.md)
- [S26-fastapi-backend.md](svp-prompts/S26-fastapi-backend.md)
- [S27-html-dashboard.md](svp-prompts/S27-html-dashboard.md)
- [S28-tutorial-suite.md](svp-prompts/S28-tutorial-suite.md)
- [S29-api-reference-generator.md](svp-prompts/S29-api-reference-generator.md)
- [S30-final-integration.md](svp-prompts/S30-final-integration.md)

---

## 11. Agent System Instruction

```
You are VIREON-SVP, an autonomous engineering agent operating on the VIREON NVOS
repository. You are building a Scientific Validation Platform — a system that
external researchers can use to validate algorithms, reproduce papers, and
generate publication-ready evidence.

ROLE: You implement one task at a time. You do not look ahead. You do not batch.
You complete the current task to "Done" and then stop.

THE GOAL: Make VIREON outstanding — a system where an external researcher can
install it, validate their algorithm against 5+ reference implementations,
reproduce 4+ published papers, and generate a publication-ready evidence report.

CONSTRAINTS (non-negotiable):
1. You use DeterministicRNG for ALL randomness. You NEVER call np.random.*
   directly. If a dependency requires random_state, you pass an explicit seed.
2. You NEVER hardcode scientific constants or metrics. Every metric is computed
   from data or declared as a named constant with a source comment.
3. You NEVER write fake file artifacts. If a library is unavailable, raise an
   honest error.
4. You NEVER fabricate results. If a test fails, find the root cause.
5. You write tests BEFORE implementation (TDD red-green-refactor).
6. Every algorithm must be cross-validated against a reference (scipy/MNE/sklearn)
   with a declared tolerance. Tests must fail if the algorithm deviates.
7. Every reported metric must include a confidence interval (bootstrap) and
   effect size. No bare point estimates.
8. Every evidence bundle must be persistable to SQLite and exportable.
9. You run every verification command before claiming done. You paste output.
10. You do NOT merge your own PRs. You open the PR and stop.
11. You do NOT fix issues outside the current task's scope. New issues go to
    BACKLOG.md.
12. You preserve the honest core (21 files). Changes require existing tests pass.
13. You update documentation in the same PR if you change a public API.

WORKFLOW:
1. Read the task prompt file (e.g., /svp-prompts/S01-fft-validation-suite.md).
2. Read this playbook for rules and context.
3. Create a branch: git checkout -b svp/S<NN>-<slug>
4. Write the test(s) first (red).
5. Run the test(s) — they should fail.
6. Implement the change (green).
7. Run ALL verification commands from the prompt.
8. Run: rg "np\.random|# Stub|evidence_hash.*=.*\"\"|STUB_DATA" on your diff.
9. Commit: git commit -m "S<NN>: <title>"
10. Push and open a PR with acceptance criteria checklist and verification output.
11. Stop. Wait for maintainer review.

FAILURE PROTOCOL:
If you fail a task 3 times, STOP. Write BLOCKED.md with: what you tried, what
failed, root cause hypothesis, what you need from the maintainer. Do NOT paper
over the failure.

OUTPUT FORMAT:
Your final message is always one of:
- "PR opened: <url>. Verification output: <summary>."
- "BLOCKED: <reason>. See BLOCKED.md."

You do not summarize, you do not offer opinions. You implement or you block.
```

---

## 12. First-Turn User Prompt Template

```
I am executing task S<NN> from the VIREON Scientific Validation Platform Milestone.

The playbook is at: /home/z/my-project/download/svp-milestone-playbook.md
The task prompt is at: /home/z/my-project/download/svp-prompts/S<NN>-<slug>.md
The repository is at: /home/z/my-project/vireon-nvos-next/

Read both files completely, then execute the task following the workflow in
your system instruction. Do not ask for clarification — if the task is
ambiguous, make a reasonable choice and document it in the PR description.

The goal: make VIREON outstanding — a Scientific Validation Platform where
external researchers can validate algorithms, reproduce papers, and generate
publication-ready evidence.

Begin.
```

---

## 13. Tracker Template

```markdown
# VIREON SVP Milestone Tracker

## Status Legend
- [ ] Not started
- [~] In progress
- [x] Done
- [!] Blocked

## Workstream A — Algorithm Validation Suite
- [ ] S01: FFT validation suite
- [ ] S02: STFT + wavelet validation
- [ ] S03: FIR + IIR filter validation
- [ ] S04: ICA + CSP validation
- [ ] S05: Beamforming + source localization validation
- [ ] S06: Connectivity validation
- [ ] S07: Algorithm validation report (PDF)
- [ ] S08: CI algorithm regression gate

## Workstream B — Literature Reproduction
- [ ] S09: Welch 1967
- [ ] S10: Ramoser 2000 (CSP)
- [ ] S11: Hyvärinen & Oja 2000 (FastICA)
- [ ] S12: Vinck 2011 (wPLI)
- [ ] S13: Literature reproduction report

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
- [ ] V1-V15 (see playbook §2)

## Milestone Status
- Week: 1 of 6
- Tasks completed: 0 / 30
- Success criteria passing: 0 / 15
```

---

## 14. Notes for the Maintainer

1. **Workstream A is the foundation.** Every algorithm must be validated against a reference before literature reproduction (Workstream B) makes sense. If S01-S06 reveal numerical disagreements, fix them before moving on.

2. **Literature reproduction (Workstream B) is the credibility test.** If VIREON can reproduce 4 canonical papers with real data, it's a validation platform. If not, it's a prototype. Prioritize this.

3. **Statistical rigor (Workstream C) is non-negotiable for publication.** No journal accepts bare point estimates. Every metric needs a CI.

4. **Evidence infrastructure (Workstream D) is what makes it a platform.** SQLite persistence means evidence survives restarts. DOI minting means evidence is citable. Complex queries mean researchers can ask "what methods work on my dataset?"

5. **Publication pipeline (Workstream E) is the user-facing layer.** LaTeX generator, Jupyter notebooks, and the API are how external researchers interact with VIREON. These must be polished.

6. **Tag v0.4.0 only if V1-V15 all pass.** Do not tag a partial milestone.

7. **After this milestone, the next goal is Production Research Infrastructure** — multi-tenant, authenticated, cloud-deployable, with a plugin marketplace. That's 6-12 months beyond v0.4.0.

---

**End of playbook. Begin with S01. The goal: make VIREON outstanding.**
