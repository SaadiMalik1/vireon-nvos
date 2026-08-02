# VIREON v0.3.0 — Research Prototype

## What Changed

This release converts VIREON from an Engineering Prototype to an Integrated Research Prototype. The defining capability — end-to-end scientific evidence generation — now works: the flagship demo produces a cryptographic evidence bundle with a real hash, a real CCC, and a PASS verdict.

## Verified Capabilities

1. **Evidence pipeline works end-to-end.** `python examples/first_validation/demo.py` produces `output/evidence.json` with:
   - Non-empty 64-char SHA-256 `evidence_hash`
   - Real computed CCC > 0 (not hardcoded)
   - `pass_fail == conclusion_verdict == "PASS"` on baseline

2. **Deterministic replay.** Same seed → same hash. Tampered bundles are detected.

3. **Native algorithm library.** Welch, FFT, STFT, wavelets, ICA, CSP, FIR, IIR, LCMV, MNE, connectivity (coherence/PLV/PLI/AEC/wPLI) — all implemented from scratch, matching scipy/MNE to machine precision (1e-7 to 1e-15).

4. **Scientific contracts enforced.** `ScientificContractViolation` raised on NaN/Inf/non-stationarity/short signals in live execution paths.

5. **Reproducible perturbations.** All perturbations use `DeterministicRNG`. No unseeded `np.random` in the execution path.

6. **Honest CLI.** `vireon verify` detects tampered bundles. `vireon reproduce <doi>` runs real reproduction or errors honestly.

7. **No fabricated results.** No `PARQUET_STUB_DATA`, no fake EDFs, no `int(total_runs * 0.05)` failure fabrication, no hardcoded CCC/accuracy/kappa.

## What's Still Missing (for Scientific Validation Platform)

- Real clinical data (currently synthetic with ERD pattern or small PhysioNet slice)
- Subgroup analysis (age, sex, pathology)
- Bias characterization
- Independent reproduction by third parties
- Published validation paper
- Regulatory profile (FDA GMLP, IEC 62304, ISO 14971)

## Test Coverage

- 224 unit and integration tests passing
- 8 integration tests verifying the end-to-end pipeline
- CI runs integration tests + doc sync checker + grep gates on every PR

## Known Limitations

- Literature tests require PhysioNet download; skip if unavailable
- BIDS conversion requires `mne_bids`; raises ImportError if missing
- BLAS capture may return None on exotic numpy configurations (never a hardcoded lie)
