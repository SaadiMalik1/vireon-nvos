### Acceptance Criteria Checklist
- [x] DECODER_STATE node with plugin calls predict() and stores result.
- [x] DECODER_STATE node without plugin logs "skipped".
- [x] predict before fit raises DecoderNotFittedError.
- [x] SklearnLDAPlugin passes isinstance(plugin, IDecoder).
- [x] pytest passes.

### Verification Output
- pytest vireon-core/tests/test_decoder_wiring.py -v passed (4 tests).
- rg "Decoder processed signal" vireon-core/ now conditional on isinstance(plugin, IDecoder).
