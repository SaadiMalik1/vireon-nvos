# Track 1 Status

| Task | Title | Status | Commit | Verification |
|------|-------|--------|--------|--------------|
| T1-1 | P0-1 FBCSP | DONE | c018d96 | `pytest vireon-methods/tests/test_fbcsp.py vireon-verification/literature/test_blankertz_2008.py -v` |
| T1-2 | P0-2 EEGNet/DeepConvNet | DONE | 2bf481f | `pytest vireon-methods/tests/test_eegnet.py vireon-methods/tests/test_deepconvnet.py vireon-verification/literature/test_lawhern_2018.py vireon-verification/literature/test_schirrmeister_2017.py -v` |
| T1-3 | P0-3 Kraskov MI | DONE | d7c6168 | `pytest vireon-methods/tests/test_mutual_information.py vireon-verification/literature/test_kraskov_2004.py -v` |
| T1-4 | P0-4 load_dataset dispatch | DONE | dd8759a | `pytest vireon-corpus/tests/ -v` |
| T1-5 | P0-5 Registry append-only | DONE | 564ffff | `pytest vireon-evidence/tests/test_registry.py -v` |
| T1-6 | P1-1 PyTorch determinism | DONE | 6fa04c9 | `pytest vireon-verification/literature/test_lawhern_2018.py::test_lawhern_2018_eegnet_deterministic -v` |
| T1-7 | P1-2 BLAS thread pinning | DONE | 5415e5d | Manual environment variable context check |
| T1-8 | P1-7 Hash gate tightening | DONE | 08707f7 | `python3 scripts/verify_hash_integrity.py` |
| T1-9 | P1-8 Transaction hash determinism | DONE | 43147b6 | `pytest vireon-evidence/tests/test_transaction_hash.py -v` |
