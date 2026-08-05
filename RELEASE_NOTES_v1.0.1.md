# VIREON v1.0.1 — Release Notes

**Tag:** `v1.0.1`  
**Release Date:** August 5, 2026  
**Status:** Zero Known Issues (Publication Ready)

---

## Key Highlights & Improvements

1. **Real Deep Learning Training Loops**:
   - Implemented real PyTorch training loops in `EEGNetWrapper` (`eegnet.py`) and `DeepConvNetWrapper` (`deepconvnet.py`) using Adam optimizer, `CrossEntropyLoss`, `DataLoader`, and epoch loops.

2. **Decoupled Architecture & Layer Violation Fixes**:
   - Extracted shared `ExperimentSchema` and `load_experiment_from_yaml` into `vireon-core/vireon_core/contracts/experiment.py`, breaking cyclic dependency between `vireon-lab` and `vireon_validation`.
   - Eliminated layer violation by removing dynamic `vireon_knowledge` import from `vireon-core/execution_engine.py`.

3. **Algorithm Reference Comparisons**:
   - Added reference comparison tests against `scipy`, `mne`, `sklearn`, and `pyriemann` baselines for Riemannian MDM, xDAWN, FBCSP, Wavelet Coherence, Transfer Entropy, Mutual Information, Laplacian, and REST.

4. **Package Exports & Metadata**:
   - Populated all 27 empty `__init__.py` files across subpackages with version constants (`__version__ = "1.0.1"`) and key symbol re-exports.
   - Completed `pyproject.toml` with license (`MIT`), README, classifiers, dependencies, and official project URLs.
   - Updated `Dockerfile` runner stage to include `RUN pip install --no-cache-dir .`.

5. **Clean Repository & Code Maintenance**:
   - Replaced Apache 2.0 headers with MIT headers in `rng.py` and `clock.py`.
   - Removed tracked binary/generated files and added `*.db` and `site/` to `.gitignore`.
   - Removed 0-byte orphan `execute_phase_a.py` and dead code (`self.rng` in `imaging.py`).
   - Cleaned up non-functional redirect stubs in `native/`.
   - Created standardized GitHub `.github/PULL_REQUEST_TEMPLATE.md`.
