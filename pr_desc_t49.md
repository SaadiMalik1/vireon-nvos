### Acceptance Criteria Checklist
- [x] `ADS1299().process(signal)` adds noise consistent with datasheet (~1 µVpp at 250 SPS).
- [x] Uses `DeterministicRNG` (not `np.random`).
- [x] Output is quantized (24-bit ADC).
- [x] No "Mock integration" in docstring.
- [x] `rg "Mock integration" vireon-models/` returns 0.

### Verification Output
Unit tests added and pass. `rg "Mock integration"` returned 0.
