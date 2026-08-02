### Acceptance Criteria Checklist
- [x] Coherence matches manual computation (`>0.5` for related, etc).
- [x] PLV of two phase-locked signals ≈ 1.0.
- [x] PLV of two independent noise signals < 0.1.
- [x] All matrices are symmetric.
- [x] Diagonal is 1.0 (self-connectivity).
- [x] NaN raises.
- [x] Native connectivity mock classes replaced with `NotImplementedError`.
- [x] No `np.random` used.

### Verification Output
- Pytest passed with coverage >= 90%.
- `rg` for `np.random` returned 0 matches in `vireon_connectivity.py`.
