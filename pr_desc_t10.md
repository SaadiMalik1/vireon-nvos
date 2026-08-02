### Acceptance Criteria Checklist
- [x] compute() matches scipy.signal.periodogram to rtol=1e-7.
- [x] Magnitude spectrum detects 10 Hz peak.
- [x] Phase spectrum is in [-π, π].
- [x] NaN raises.
- [x] No np.random, no scipy.signal.periodogram.
- [x] pytest passes.

### Verification Output
- Pytest passed.
- `rg` for `np.random` returned 0 matches.
