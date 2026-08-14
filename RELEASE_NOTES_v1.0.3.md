# VIREON v1.0.3 — Release Notes

**Tag:** `v1.0.3`  
**Release Date:** August 6, 2026  
**Status:** Zero Known Issues / Multi-Platform Hardware Acceleration Ready

---

## Key Deliverables & Improvements

1. **Real Deep Learning Training Loops & GPU Acceleration**:
   - `EEGNetWrapper` & `DeepConvNetWrapper` PyTorch training loops with Adam optimizer, CrossEntropyLoss, DataLoader, and automatic hardware acceleration detection (`CUDA`, `ROCm`, `MPS`, `CPU`).

2. **Decoupled Architecture**:
   - Extracted `ExperimentSchema` & `load_experiment_from_yaml` into `vireon-core/vireon_core/contracts/experiment.py`, breaking cyclic dependency between `vireon-lab` and `vireon-validation`.

3. **Multi-Platform Hardware Detection**:
   - Added `vireon_core.runtime.hardware` module for auto-detecting NVIDIA CUDA, AMD ROCm, Apple Silicon Metal (MPS), and CPU backends without requiring explicit user configuration.
   - Evidence bundles now record GPU vendor, model, driver version, and VRAM memory in environment provenance fingerprints.

4. **8 New Algorithm Reference Comparisons**:
   - Validated Riemannian MDM, xDAWN, FBCSP, Wavelet Coherence, Transfer Entropy, Mutual Information, Spatial Laplacian, and REST against SciPy / Sklearn / PyRiemann / analytical baselines.

5. **Package Metadata & Repo Hygiene**:
   - Updated `pyproject.toml` version to `1.0.3` with complete PyPI metadata, optional dependencies (`gpu`, `deep-learning`, `dev`), and `vireon` CLI script entry point.
   - Updated `Dockerfile` runner stage to install package.
   - Fixed unseeded RNG calls in tests.
   - Created `.github/PULL_REQUEST_TEMPLATE.md`.
   - Unified runtime license headers to MIT.
   - Implemented real Fast Gradient Sign Method (FGSM) adversarial robustness attack example.
   - Expanded SOUP inventory with all 16 external dependencies.
