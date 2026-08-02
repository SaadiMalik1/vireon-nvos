### Acceptance Criteria Checklist
- [x] `convert_to_bids()` creates a valid BIDS dataset using `mne_bids`.
- [x] `channels.tsv` is written with channel names, types, units.
- [x] `events.tsv` is written with onset, duration, type.
- [x] `participants.tsv` is written.
- [x] `*_eeg.json` sidecar is generated.

### Verification Output
- Test in `test_bids_conversion.py` passes.
- Fallback paths defined if `mne_bids` is not installed.
