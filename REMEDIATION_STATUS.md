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
| P1-3 | Wire the GPU API | PENDING | — | — |
| P1-4 | Implement MassiveCampaignOrchestrator | PENDING | — | — |
