# ADR 0008: VIREON × MOABB Integration

**Date:** 2026-08-11
**Status:** ACCEPTED
**Supersedes:** ADR 0001 (validation-not-simulation) — refines, does not replace

## Context

VIREON v1.0.3 maintains 22 native algorithm implementations, 7 dataset loaders, and its own benchmark/evaluation infrastructure. The audit (S4, S12, S20) found:

- 7 algorithm correctness bugs (FBCSP broken, EEGNet/DeepConvNet architectures incomplete, MI mislabeled, etc.)
- All 7 dataset keys return identical data (load_dataset ignores the key parameter)
- 16 of 33 algorithm files are thin scipy/sklearn wrappers that add no value

Meanwhile, MOABB (v1.5.0, NeuroTechX) is a mature, community-maintained framework that already solves the BCI benchmarking problem: datasets, paradigms, pipelines, cross-session/cross-subject evaluation. Maintaining VIREON's parallel implementation is both expensive (correctness bugs to fix) and strategically wrong (competing with mature libraries rather than building on top of them).

## Decision

VIREON will integrate with MOABB as a delegation backend. VIREON owns the validation/evidence layer; MOABB owns the BCI execution layer.

## The 10 Principles (Frozen)

1. **VIREON does not reimplement MOABB functionality.** No native BCI datasets, paradigms, pipelines, or evaluation strategies. Use MOABB's.

2. **MOABB owns BCI datasets/paradigms/pipelines/evaluation.** VIREON does not duplicate `BNCI2014_001`, `LeftRightImagery`, `LogVariance+LDA`, or `CrossSessionEvaluation`.

3. **VIREON owns experiment specification.** `ExperimentSpec` is the architectural contract. It specifies what to run; MOABB executes it.

4. **VIREON may instrument execution for validation.** VIREON is not limited to consuming MOABB's final accuracy. It can observe dataset metadata, execution partitions, and intermediate results for leakage detection, inspection, and provenance.

5. **VIREON owns statistical validation beyond MOABB's scope.** Subject-level bootstrap CIs (not trial-level — avoids pseudoreplication), permutation tests that respect experimental structure, effect sizes.

6. **VIREON owns perturbation/robustness experiments.** VIREON modifies experimental conditions (channel dropout, noise injection) and re-executes via MOABB. VIREON does not perturb results post-hoc.

7. **VIREON owns provenance/evidence.** Dataset hashes, pipeline hashes, environment fingerprints, seeds, execution traces → SHA-256 EvidenceBundle.

8. **Every evidence claim must trace to an execution artifact.** No hardcoded metrics. No fake hashes. No "ccc=1.0" without a real comparison. If VIREON claims it, VIREON must have executed it.

9. **No scorecard until underlying evidence is complete.** The first POC produces a raw evidence report (dataset, validation, statistics, robustness, provenance, evidence hash). Scorecards come later, only after every dimension is verified to be real.

10. **Native algorithm implementations are deprecated.** Moved to `vireon-methods/reference/deprecated/`. Not deleted — kept for regression testing, differential testing, and archaeology. Removed in v2.0.

## Architecture

```
                         VIREON
                           │
                    ExperimentSpec
                           │
                ┌──────────┴──────────┐
                │                     │
                ▼                     ▼
          Intent/Policy         Execution Plan
                │                     │
                └──────────┬──────────┘
                           ▼
                  Scientific Adapters
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
        MOABB             MNE          sklearn/PyTorch
          │                │                │
          └────────────────┼────────────────┘
                           ▼
                    Execution Trace
                           │
             ┌─────────────┼──────────────┐
             ▼             ▼              ▼
         Validation    Robustness     Reference
             │             │              │
             └─────────────┼──────────────┘
                           ▼
                       Statistics
                           │
                           ▼
                    Evidence Engine
                           │
                 ┌─────────┴─────────┐
                 ▼                   ▼
             Provenance          Knowledge Graph
                 │                   │
                 └─────────┬─────────┘
                           ▼
                     Decision Engine
                           │
                           ▼
                Report / Scorecard / API
```

## Validation Hooks (Principle 4 in detail)

VIREON does not "never touch the data." It observes and instruments:

| VIREON need | What it accesses | How |
|---|---|---|
| Leakage detection | Subject IDs, session IDs, train/test membership | MOABB evaluation exposes partitions |
| Channel dropout robustness | Raw epoch data | VIREON perturbs data, MOABB re-executes |
| White-noise robustness | Raw epoch data | Same |
| Line-noise robustness | Raw epoch data | Same |
| Dataset inspection | NaNs, flat channels, clipping, DC drift | VIREON reads MOABB dataset object |
| Provenance | Dataset hash, pipeline code, environment | VIREON captures at execution time |

VIREON does not **own** the EEG processing. It **observes/instruments** it.

## Reference Comparison (Principle — corrected)

Reference comparisons must be at the **correct computational boundary**:

| VIREON operation | Reference | Valid? |
|---|---|---|
| VireonWelch | scipy.signal.welch | ✓ (if VIREON has a Welch impl) |
| VireonCSP | mne.decoding.CSP | ✓ (if VIREON has a CSP impl) |
| VireonICA | sklearn.decomposition.FastICA | ✓ |
| LogVariance (MOABB) | scipy.signal.welch bandpower | ✗ — different computations, no valid equivalence |

If VIREON delegates to MOABB/MNE/scipy, there may be no reason for a parallel VIREON implementation, and therefore no need for reference comparison. Reference comparison is for when VIREON has its own implementation; in the MOABB integration, MOABB IS the reference.

## Statistics Semantics (Principle 5 in detail)

With BNCI2014_001 (9 subjects), bootstrapping individual trials creates pseudoreplication — observations within subjects aren't independent. VIREON's statistical layer must:

- **Bootstrap by subject**, not by trial. Resample the 9 subject-level accuracies, not the individual trial predictions.
- **Permutation tests respect experimental structure.** Shuffle labels at the appropriate level (subject or session, depending on the hypothesis).
- **Know what statistical question is being asked.** VIREON's statistics layer should understand: "What is the independent unit?" "Is the resampling scheme compatible with the evaluation design?"

This is a genuine VIREON differentiator — MOABB runs the benchmark; VIREON ensures the statistics are scientifically valid.

## POC Success Criterion (Frozen)

> Given a standard MOABB experiment, VIREON produces an independently verifiable evidence bundle in which every reported scientific claim can be traced to a specific dataset, execution, parameterization, statistical procedure, software version, and validation result.

NOT: "VIREON produces a score of 91/100."

The first POC produces a **raw evidence report** (no scorecard). Scorecards come only after every evidence dimension is verified to be real.

## Consequences

- `vireon-methods/vireon_methods/` native implementations → deprecated to `reference/deprecated/`
- `vireon-corpus/` dataset loaders → replaced by MOABB adapter
- `vireon-moabb/` new package → MoabbExecutor, ValidationLayer, EvidenceAssembler, Reporter
- Marketing changes: "22 native algorithms" → "validates neurotechnology workflows using established scientific libraries"
- ~3,600 LOC of native algorithm code moves to deprecated/
- Agent A (algorithms) in the multi-agent playbook → mostly eliminated
- Agent B (datasets) → rewritten as MOABB integration
