# VIREON Remediation Status

| Task ID | Title | Status | Commit | Notes |
|---------|-------|--------|--------|-------|
| P0-1 | Fix VireonFBCSP to Apply Band-Pass Filters Per Band | DONE | c018d96 | Applied bandpass filters per frequency band before CSP feature extraction |
| P0-2 | Complete EEGNet Architecture Implementation | DONE | 2bf481f | Completed EEGNet (Lawhern 2018) and DeepConvNet (Schirrmeister 2017) architectures |
| P0-3 | Fix Signal Metrics Window Overlap Formula | PENDING | — | — |
| P0-4 | Fix DatasetManager Path Traversal & Key Dispatch Bug | DONE | dd8759a | Rewrote DatasetManager.load_dataset to dispatch by key without silent synthetic fallbacks |
| P0-5 | Replace INSERT OR REPLACE with INSERT OR IGNORE in Evidence Registry | DONE | 564ffff | Replaced INSERT OR REPLACE with INSERT OR IGNORE, added EvidenceAlreadyRegisteredError and update_bundle append-only path |
| P0-6 | Replace Regulatory Submission Stub with Substantive Binder Generator | DONE | bb677e2 | Implemented RegulatoryBinderGenerator generating 9-file audit binder, updated VMP §10.1 |
| P0-7 | Implement Real Transfer Entropy with Past Conditioning | PENDING | — | — |
| P0-8 | Implement Real Mutual Information (Kraskov KSG Estimator) | DONE | d7c6168 | Implemented Kraskov 2004 k-NN MI estimator |
| P0-9 | Fix Benchmark Matrix Metric Hash Determination | PENDING | — | — |
| P0-10 | Add Leadfield Matrix Validation to MinimumNorm and LCMV | PENDING | — | — |
| P0-11 | Fix Replay Engine Command Line Path Resolution | PENDING | — | — |
| P0-12 | Fix REST Re-referencing Singular Value Regularization | PENDING | — | — |

## Phase 2: Significant Defects (P1)

| Task ID | Title | Status | Commit | Notes |
|---------|-------|--------|--------|-------|
| P1-1 | Add PyTorch Determinism Settings | DONE | 6fa04c9 | Added manual_seed, cudnn.deterministic, cudnn.benchmark, deterministic_algorithms, seeded DataLoader |
| P1-2 | Pin BLAS Threads via threadpoolctl | DONE | 5415e5d | Added pinned_blas_threads context manager and blas_thread_count field |
| P1-3 | Wire the GPU API | DONE | e4b09b7 | Wired get_torch_device, is_gpu_available, and to_device into EEGNet & DeepConvNet wrappers with CLI --gpu flag |
| P1-4 | Implement MassiveCampaignOrchestrator | DONE | 2572ed3 | Implemented Cartesian campaign execution with EvidenceRegistry and FailureAtlas integration |
| P1-5 | Fill 35 Empty Doc Stubs | DONE | 4af877d | Filled all 35 Phase E documentation stubs with family-specific status notes |
| P1-6 | Make FastAPI Deployable | DONE | 7adb749 | Added uvicorn runner, multi-stage Dockerfile, API key auth, CORS config, and v1.1.0 sync |
| P1-7 | Tighten CI Grep Gate for Fake Hashes | DONE | 08707f7 | Multi-pattern grep check & AST verify_hash_integrity.py added; fake hash placeholders removed |
| P1-8 | Replace Transaction Timestamp with Counter | DONE | 43147b6 | Replaced wall-clock hash inclusion with deterministic transaction payload and sequence counter |
| P2-1 | Add Linting, Type-checking & Coverage Config | DONE | 4b7b24a | Configured ruff, mypy, and coverage sections in pyproject.toml and added CI lint job |
| P2-2 | Remove Committed Binary State | DONE | 1bf0015 | Untracked binary DBs, site/ HTML, telemetry outputs; added scripts/regenerate_seed_registry.py |
| P2-3 | Sync API Documentation with Implementation | DONE | 853ffa4 | Generated docs/api_reference.md, corrected Ramoser 2000 DOI, updated STATUS.md to v1.1.0 |
| P2-4 | Consolidate Duplicated Implementations | DONE | 3605e3a | Deprecated WelchPSDPlugin, CSPPlugin, and ICAPlugin wrappers with DeprecationWarning; re-exported native classes |
| P2-5 | Pin Upper Bounds on Dependencies | DONE | 812405a | Added upper bound constraints (<2.0.0, <3.0.0, etc.) in pyproject.toml and requirements.txt |
| P2-6 | Delete Root Scratch Files | DONE | 77d7df9 | Removed scratch_bids.py, parse_phase_c.py, parse_transcript.py, and test_bem.py |
| P2-7 | Sync Subpackage __version__ Strings | DONE | fc4b332 | Synced 26 __init__.py subpackage version strings to 1.1.0 using scripts/sync_subpackage_versions.py |
| P2-8 | Add Security Disclosure Policy | DONE | 8b69f03 | Added SECURITY.md with version support table and responsible disclosure guidelines |
| P2-9 | Add Community Code of Conduct | DONE | e225563 | Added CODE_OF_CONDUCT.md adopting Contributor Covenant 2.1 |

## Phase 4: Enhancements (P4)

| Task ID | Title | Status | Commit | Notes |
|---------|-------|--------|--------|-------|
| P4-1 | Add MNE-Python Compatibility Layer | DONE | bd53084 | Added mne_to_vireon and vireon_to_mne converters in vireon_core.compat.mne_adapter |
| P4-3 | Expand Knowledge Graph Rule Coverage | DONE | 8969d90 | Expanded rules.jsonld with FIR, CSP, and WaveletCoherence rules and added assumptions.jsonld |
