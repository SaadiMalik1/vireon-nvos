# Study C Protocol — Blind Real-World Validation of VIREON

**Status:** PREREGISTERED
**Date:** 2026-08-16
**Version:** 1.0 (frozen — do not modify after first experiment)
**Principal Investigator:** [To be filled]
**Independent Adjudicator:** [To be filled — must not have built VIREON's validation logic]

---

## 1. Research Question

> **Can an automated, execution-aware validation framework identify scientifically meaningful methodological concerns in computational neurotechnology experiments beyond conventional benchmark performance?**

## 2. Primary Endpoint

> **The proportion of VIREON-generated V2/V3 findings that are independently adjudicated as genuine methodological concerns.**

## 3. Secondary Endpoints

1. Reproduction success rate: proportion of experiments where MOABB reconstruction matches the published result (±5%)
2. V1 rate: proportion of experiments where VIREON adds useful characterization without identifying concerns
3. V0 rate: proportion of experiments where VIREON confirms the benchmark with no additional concerns
4. False discovery rate: proportion of V2 findings that adjudicators reject
5. Sensitivity: proportion of known methodological issues (identified post-hoc by adjudicator) that VIREON independently flagged

## 4. Study Population

Published computational BCI/neurotechnology experiments that:
- Use EEG-based BCI paradigms (motor imagery, P300, SSVEP)
- Report classification accuracy or equivalent performance metric
- Use datasets available through MOABB or MNE
- Have sufficient methodological detail to reconstruct the pipeline
- Were published in a peer-reviewed venue

## 5. Selection Criteria (Pre-specified)

Experiments are selected using a **predefined sampling matrix** before VIREON evaluates them:

| ID | Paradigm | Method Family | Dataset | Pipeline |
|----|----------|---------------|---------|----------|
| C-1 | Motor imagery | Classical (CSP+LDA) | BNCI2014_001 | CSP(n=8) + LDA, CrossSession |
| C-2 | Motor imagery | Deep learning | BNCI2014_001 | EEGNet (or LogVar+LogReg if PyTorch unavailable), CrossSession |
| C-3 | Motor imagery | Riemannian | BNCI2014_001 | MDM (covariance + tangent space), CrossSession |
| C-4 | P300 | Classical decoder | EPFLP300 | LogVariance + LogisticRegression, WithinSession |
| C-5 | SSVEP | Frequency-domain | Wang2016 | LogVariance + LogisticRegression, WithinSession |

**Protocol Amendment (2026-08-16):** C-4 and C-5 originally specified BNCI2015_001 and BNCI2015_004, respectively. These datasets are motor imagery, not P300/SSVEP. Replaced with EPFLP300 (paradigm=p300) and Wang2016 (paradigm=ssvep), which are the correct paradigm-specific datasets. VIREON validation code unchanged.

**Selection rule:** The specific pipeline for each cell is chosen from the MOABB benchmark corpus BEFORE running VIREON. No experiment is selected because VIREON is expected to find (or not find) a problem.

## 6. Exclusion Criteria

An experiment is excluded if:
- The dataset cannot be loaded via MOABB (network failure, corrupted data)
- The pipeline cannot be reconstructed from available information
- MOABB execution fails after 3 retry attempts
- The experiment requires proprietary data or software

Excluded experiments are replaced with the next available option from the same sampling matrix cell.

## 7. Reconstruction Protocol

For each experiment:
1. Identify the dataset, paradigm, pipeline, and evaluation strategy from published information
2. Reconstruct using MOABB's standard implementations (no custom code)
3. Record: accuracy per subject, mean accuracy, runtime, environment
4. Compare reproduced accuracy to published accuracy (±5% tolerance for reproduction success)

## 8. VIREON Validation Protocol

For each experiment, run VIREON's validation layer with **no modifications during the study**:
1. Build ExperimentSpec with the reconstructed pipeline
2. Execute via MoabbExecutor (captures execution trace)
3. Run ValidationLayer (partition integrity, statistics, reproducibility)
4. Run robustness perturbations (3 types: channel dropout, white noise, line noise)
5. Generate EvidenceBundle with SHA-256
6. Produce Validation Profile

**Critical:** VIREON's validation code is FROZEN for the duration of Study C. No changes to validation logic between experiments. If a bug is discovered, it is documented but not fixed until all 5 experiments are complete.

## 9. V0-V3 Finding Classification

### V0 — No additional concern

VIREON reproduces the benchmark and finds no substantive methodological issue. All validation checks pass. The evidence bundle confirms the result is reproducible and well-characterized.

### V1 — Additional characterization

VIREON adds scientifically useful information (uncertainty quantification, statistical significance, robustness profile, provenance) without identifying an invalid method. The benchmark result is confirmed, and VIREON enriches it with additional evidence.

### V2 — Potential methodological concern

VIREON flags something that warrants expert review. This includes:
- Detected partition overlap (subject/session leakage)
- Below-chance performance in any fold
- Missing reproducibility metadata
- Robustness degradation exceeding predefined threshold (>15% accuracy drop)
- Statistical unit mismatch
- Evidence integrity issues

VIREON does NOT declare the paper wrong — it flags the concern for adjudication.

### V3 — Independently confirmed problem

An independent adjudicator examines the evidence and concludes the concern is genuine. This requires:
- The VIREON finding is technically reproducible
- The finding is scientifically meaningful (not an artifact of VIREON's implementation)
- The issue would affect interpretation of the original result

**V3 is the key outcome for the research thesis.**

## 10. Adjudication Protocol

### Adjudicator requirements
- Must not have contributed to VIREON's validation logic
- Must have domain expertise in BCI/EEG research
- Reviews findings BLIND to VIREON's internal reasoning (sees only the evidence, not the implementation)

### Adjudication form (per finding)

```
EXPERIMENT ID: C-__
FINDING ID: F-__
PAPER: [citation]
DATASET: [name]
PIPELINE: [description]

VIREON FINDING:
  [description of what VIREON detected]

RELEVANT EVIDENCE:
  [evidence bundle hash, execution trace excerpt, statistical output]

QUESTIONS FOR ADJUDICATOR:

1. Is the finding technically reproducible?
   [ ] Yes  [ ] No  [ ] Insufficient evidence

2. Is the finding scientifically meaningful?
   [ ] Yes  [ ] No  [ ] Insufficient evidence

3. Is it a genuine methodological concern?
   [ ] Yes  [ ] No  [ ] Insufficient evidence

4. Is the evidence sufficient to support the finding?
   [ ] Yes  [ ] No  [ ] Insufficient evidence

5. What is the severity?
   [ ] Critical (invalidates the result)
   [ ] Major (affects interpretation)
   [ ] Minor (worth noting)
   [ ] Not a concern

6. Would the issue affect interpretation of the original result?
   [ ] Yes  [ ] No  [ ] Uncertain

ADJUDICATOR VERDICT:
   [ ] Confirmed (genuine methodological issue)
   [ ] Partially confirmed (issue exists but limited impact)
   [ ] Not confirmed (not a genuine concern)
   [ ] Insufficient evidence (cannot adjudicate)

ADJUDICATOR COMMENTS:
   [free text]
```

### Adjudication rules
- The adjudicator sees the **evidence** (execution trace, statistics, partition data) but NOT VIREON's source code or implementation details
- The adjudicator may request additional information but may not re-run VIREON with modified parameters
- If the adjudicator requests a re-run, it must use the SAME frozen VIREON version
- Disagreements between VIREON's verdict and the adjudicator's verdict are recorded, not resolved by modifying VIREON

## 11. Handling of Failed Reproductions

If MOABB reconstruction fails (accuracy differs from published by >5%):
1. Document the discrepancy
2. Check for: different preprocessing, different evaluation protocol, different data version
3. If the discrepancy cannot be resolved, classify as "reproduction failure" and note it
4. VIREON validation still runs on the reproduced result (even if it doesn't match the paper)
5. The adjudicator reviews the reproduction discrepancy as a potential finding

## 12. Statistical Analysis

After all 5 experiments + adjudications:

```
Primary endpoint:
  V3 rate = (number of V3-confirmed findings) / (total V2 findings)

Secondary:
  Reproduction rate = (experiments with <5% accuracy difference) / 5
  V0 rate = (experiments with no V1-V3 findings) / 5
  V1 rate = (experiments with V1 findings only) / 5
  V2 rate = (experiments with V2 findings) / 5
  False discovery rate = (V2 findings rejected by adjudicator) / (total V2 findings)
```

With n=5, this is descriptive only — no inferential statistics. The study establishes feasibility and direction, not statistical significance.

## 13. Pre-registration Commitments

The following are frozen before C-2 begins:

1. Selection criteria (Section 5)
2. V0-V3 definitions (Section 9)
3. Adjudication protocol (Section 10)
4. VIREON validation code (no modifications between experiments)
5. Robustness thresholds (>15% drop = V2 concern)
6. Statistical unit (subject-level for all bootstrap/permutation)
7. Reproduction tolerance (±5% accuracy)

**These will not be modified because of results from any experiment.**

If a modification is scientifically necessary (e.g., discovering that ±5% is too strict), it is documented as a protocol amendment with rationale, and all experiments are re-run with the new protocol.

## 14. Data Management

For each experiment:
- Evidence bundle (JSON with SHA-256 hash)
- Execution trace (complete MOABB output)
- Validation profile (text report)
- Adjudication form (completed)
- Raw MOABB results (CSV)

All stored in `study_c/experiment_C-N/` with the evidence bundle as the canonical artifact.

## 15. Timeline

| Phase | Activity | Duration |
|-------|----------|----------|
| 1 | Protocol finalization (this document) | Complete |
| 2 | Partition semantics fix (Study-C-blocking) | 1 day |
| 3 | C-1 packaging (existing experiment) | 1 day |
| 4 | C-2 through C-5 execution | 1-2 weeks |
| 5 | Independent adjudication | 1-2 weeks |
| 6 | Analysis and report | 1 week |

## 16. Expected Limitations

1. **Small sample (n=5):** This study establishes feasibility and direction, not statistical power. A larger corpus (n=20-50) would be needed for quantitative claims about detection rates.

2. **Single adjudicator:** Ideally, multiple adjudicators with inter-rater reliability. This study uses one for feasibility.

3. **MOABB-only reconstruction:** Only experiments reproducible via MOABB are included. Experiments requiring custom code or proprietary data are excluded.

4. **VIREON version frozen:** Bugs discovered during the study are documented but not fixed. This means VIREON's performance in this study is a lower bound on its potential performance.

5. **No ground truth for "no problem":** When VIREON says PASS, we cannot independently verify that no problem exists — we can only verify that VIREON didn't find one.
