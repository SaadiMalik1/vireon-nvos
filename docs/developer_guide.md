# VIREON Developer & Contributor Architecture Manual (v1.0.0)

---

## 1. Architectural Philosophy & Monorepo Design

VIREON is engineered as a high-integrity, modular monorepo structured into 10 decoupled packages:

1. `vireon-core`: Contracts, interfaces, `EvidenceBundle` schemas, `DeterministicRNG` runtime, and plugin registries.
2. `vireon-models`: Core numerical data structures and signal representations.
3. `vireon-methods`: Signal processing, spectral analysis, spatial filtering, connectivity, source localization, and deep learning wrappers.
4. `vireon-validation`: Statistical concordance metrics (Lin's CCC, ICC(3,1)), perturbation stress matrix, and reference validation.
5. `vireon-evidence`: SQLite `EvidenceGraph`, evidence registry, cryptographic hashing engines, and multi-format exporters (Markdown, JSON-LD, LaTeX).
6. `vireon-knowledge`: Domain knowledge graphs, literature citation metadata, and paper reproduction specifications.
7. `vireon-corpus`: DatasetManager, open EEG dataset download engines, local disk caching (`~/.vireon/datasets/`), and checksum verification.
8. `vireon-lab`: Experimental benchmarking runners and research workflows.
9. `vireon-api`: Fast-API REST endpoints and RPC service wrappers for external software integration.
10. `vireon-verification`: Automated literature reproduction test suite and compliance verification gates.

---

## 2. Developer Environment Setup

To set up a local development environment:

```bash
# 1. Clone repository
git clone https://github.com/SaadiMalik1/vireon-nvos.git
cd vireon-nvos

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install in editable mode with development dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install hypothesis pytest pytest-cov mkdocs mkdocs-material
pip install -e .

# 4. Run test suite to verify installation
pytest --tb=short -q
```

---

## 3. Strict Operating Rules for Developers & AI Agents

All contributions must strictly adhere to the 15 VIREON Agent System Instruction Rules:

1. **R1: Real Data First**: Real physiological EEG datasets must be used for literature test cases and benchmarks whenever available.
2. **R2: Test-Driven Development (TDD)**: Always write tests before writing implementation code. (Red $\rightarrow$ Green $\rightarrow$ Refactor).
3. **R3: Deterministic Randomness**: NEVER use `np.random.*` directly. ALL randomness MUST be generated using `DeterministicRNG(seed)`.
4. **R4: No Hardcoded Constants**: Every metric must be dynamically computed from physiological data.
5. **R5: Honest Core Preservation**: The 21 core architectural files are off-limits to breaking API changes without formal RFC review.
6. **R6: Numerical Cross-Validation**: Every algorithm MUST be cross-validated against a standard reference library (`scipy`, `MNE-Python`, `scikit-learn`) with Lin's $CCC \ge 0.99$.
7. **R7: One PR Per Task**: Create isolated task branches (`abc/R<NN>-<slug>`, `abc/W<NN>-<slug>`, `abc/P<NN>-<slug>`).
8. **R8: Evidence Persistence**: Every evidence bundle must be persistable to SQLite and exportable to JSON-LD / LaTeX.
9. **R9: Statistical Rigor**: All reported point estimates must include $95\%$ bootstrap confidence intervals and effect sizes.
10. **R10: Mandatory DOI Citation**: Every paper reproduction test must cite its DOI in the file docstring.

---

## 4. Developing New Algorithm Modules in `vireon-methods`

To add a new algorithm module to `vireon-methods`, follow this standardized step-by-step workflow:

### Step 1: Create Module File
Create the module in the appropriate subpackage (e.g., `vireon-methods/vireon_methods/spatial/vireon_myalgo.py`).

```python
"""My Algorithm Module Description.

Reference: Author et al. (Year). Title. Journal. DOI: 10.xxxx/xxxx
"""
import numpy as np
from vireon_core.runtime.rng import DeterministicRNG

class VireonMyAlgorithm:
    """Mathematical algorithm description."""
    def __init__(self, param: float = 1.0):
        self.param = param
        
    def fit_transform(self, X: np.ndarray, y: np.ndarray) -> np.ndarray:
        # Implementation using DeterministicRNG if randomness is needed
        return X * self.param
```

### Step 2: Implement Reference Validation Test
Create a validation test under `tests/test_algorithm_validation_suite/` comparing your implementation against a reference standard using Lin's CCC:

```python
from vireon_validation.statistics.framework import lin_concordance_correlation

def test_my_algorithm_reference_match():
    # Execute VIREON implementation vs reference
    ccc = lin_concordance_correlation(vireon_output, reference_output)
    assert ccc >= 0.99, f"CCC {ccc:.6f} < 0.99 threshold"
```

---

## 5. Continuous Integration (CI/CD) & Automated Grep Gates

The VIREON CI pipeline (`.github/workflows/ci.yml`) enforces automated quality gates on every push:

```bash
# Run unit test suite
pytest --tb=short -q

# Run automated grep gates
! rg 'evidence_hash\s*=\s*""' vireon-validation/ vireon-core/
! rg "PARQUET_STUB_DATA" vireon-validation/
! rg "np\.random\.(normal|uniform|choice)" vireon-validation/vireon_validation/perturbations/
```

---

## 6. Detailed Mathematical Verification Frameworks

### 6.1 Lin's Concordance Correlation Coefficient ($CCC$)
$$\rho_c = \frac{2 s_{xy}}{s_x^2 + s_y^2 + (\bar{x} - \bar{y})^2}$$

### 6.2 Intraclass Correlation Coefficient $ICC(3,1)$
$$ICC(3,1) = \frac{MS_S - MS_E}{MS_S + (k - 1) MS_E}$$

### 6.3 Percentile Bootstrap Confidence Intervals
To compute non-parametric $95\%$ confidence intervals, VIREON draws 1,000 bootstrap resamples with replacement using `DeterministicRNG`:

```python
from vireon_core.runtime.rng import DeterministicRNG

def bootstrap_ci(data: np.ndarray, n_boot: int = 1000, ci: float = 95.0, seed: int = 42):
    rng = DeterministicRNG(seed)
    boot_means = []
    n = len(data)
    for _ in range(n_boot):
        idx = rng.uniform(0, n, n).astype(int)
        boot_means.append(np.mean(data[idx]))
    low = np.percentile(boot_means, (100 - ci) / 2)
    high = np.percentile(boot_means, 100 - (100 - ci) / 2)
    return float(low), float(high)
```

---

## 7. Multi-Package Dependency Graph & Internal Imports

```
                   +------------------------+
                   |      vireon-core       |
                   +------------------------+
                               |
                               v
                   +------------------------+
                   |     vireon-models      |
                   +------------------------+
                               |
                               v
                   +------------------------+
                   |     vireon-methods     |
                   +------------------------+
                   /           |            \
                  /            v             \
  +------------------+ +----------------+ +------------------+
  | vireon-validation| | vireon-evidence| |  vireon-corpus   |
  +------------------+ +----------------+ +------------------+
                  \            |            /
                   v           v           v
                   +------------------------+
                   |  vireon-verification   |
                   +------------------------+
```

---

## 8. Release Process & Semantic Versioning

VIREON follows Semantic Versioning 2.0.0 (`MAJOR.MINOR.PATCH`):
- **Patch Release (`v1.0.1`)**: Backward-compatible bug fixes and doc updates.
- **Minor Release (`v1.1.0`)**: Backward-compatible new algorithms or datasets.
- **Major Release (`v2.0.0`)**: Breaking API contract changes.

```bash
# Tagging release
git tag -a v1.0.0 -m "VIREON v1.0.0 Release — Real Data Integration, 22 Algorithms, 29 Papers"
git push origin v1.0.0
```

---

## 10. Deep-Dive Core File Preservations (The 21 Honest-Core Files)

To preserve architectural integrity and avoid unexpected regressions (Rule R9), the following 21 files represent the "Honest Core" of VIREON and are subject to mandatory backward-compatibility checks:

1. `vireon-core/vireon_core/contracts/base.py`: Fundamental signal and interface definitions.
2. `vireon-core/vireon_core/contracts/evidence.py`: Pydantic `EvidenceBundle` schema definitions.
3. `vireon-core/vireon_core/runtime/rng.py`: `DeterministicRNG` seed-locked random number generator.
4. `vireon-core/vireon_core/kernel/plugins.py`: Plugin loader and discovery engine.
5. `vireon-core/vireon_core/contracts/base.py`: Core signal contracts, interface specifications, and execution DAG containers.
6. `vireon-methods/vireon_methods/spectral/vireon_welch.py`: Native Welch PSD implementation.
7. `vireon-methods/vireon_methods/spectral/vireon_multitaper.py`: Native Thomson Multitaper implementation.
8. `vireon-methods/vireon_methods/spatial/vireon_csp.py`: Native Common Spatial Pattern filter.
9. `vireon-methods/vireon_methods/spatial/vireon_ica.py`: Native FastICA implementation.
10. `vireon-methods/vireon_methods/connectivity/vireon_connectivity.py`: Native WPLI & AEC functions.
11. `vireon-methods/vireon_methods/source_localization/vireon_beamforming.py`: Native LCMV beamformer.
12. `vireon-methods/vireon_methods/source_localization/vireon_source_localization.py`: Native MNE/sLORETA solver.
13. `vireon-validation/vireon_validation/statistics/framework.py`: Lin's CCC implementation.
14. `vireon-validation/vireon_validation/statistics/icc.py`: Shrout & Fleiss ICC implementation.
15. `vireon-validation/vireon_validation/benchmarks/matrix.py`: Perturbation matrix runner.
16. `vireon-evidence/vireon_evidence/registry/core.py`: SQLite evidence registry engine.
17. `vireon-evidence/vireon_evidence/graph/core.py`: Evidence network graph builder.
18. `vireon-corpus/vireon_corpus/dataset_manager.py`: Dataset manager and disk caching engine.
19. `vireon-api/vireon_api/main.py`: FastAPI server routes and endpoints.
20. `vireon-verification/literature/test_welch_1967.py`: Welch 1967 paper reproduction test.
21. `vireon-verification/literature/test_ramoser_2000.py`: Ramoser 2000 CSP paper reproduction test.

---

## 11. Detailed Plugin SDK System Architecture

VIREON provides an extensible Plugin SDK that allows external research groups and third-party commercial developers to integrate custom signal processing methods or dataset loaders without modifying VIREON core code.

### 11.1 Plugin Contract Specification
```python
from vireon_core.contracts.base import ISignal
from typing import Dict, Any

class IVireonPlugin:
    """Base interface for all third-party VIREON plugins."""
    
    @property
    def plugin_name(self) -> str:
        """Return unique plugin identifier name."""
        raise NotImplementedError
        
    @property
    def plugin_version(self) -> str:
        """Return semantic version string."""
        raise NotImplementedError
        
    def execute(self, signal: ISignal, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute plugin processing logic and return output payload."""
        raise NotImplementedError
```

### 11.2 Registering Plugins via Setuptools Entry Points
To expose a custom plugin to VIREON's automatic discovery engine, register it in your plugin's `pyproject.toml`:

```toml
[project.entry-points."vireon.plugins"]
my_custom_plugin = "my_package.plugin_module:MyCustomPluginClass"
```

---

## 12. SQLite Evidence Registry Schema Specification

All evidence bundles generated by VIREON are stored in `evidence_registry.db` under the following SQL schema:

```sql
CREATE TABLE IF NOT EXISTS evidence_bundles (
    bundle_id TEXT PRIMARY KEY,
    evidence_hash TEXT NOT NULL UNIQUE,
    timestamp TEXT NOT NULL,
    algorithm TEXT NOT NULL,
    dataset TEXT NOT NULL,
    statistical_agreement_json TEXT NOT NULL,
    runtime_sec REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_evidence_hash ON evidence_bundles(evidence_hash);
CREATE INDEX IF NOT EXISTS idx_algorithm ON evidence_bundles(algorithm);
CREATE INDEX IF NOT EXISTS idx_dataset ON evidence_bundles(dataset);
```

---

## 13. REST API & RPC Microservice Specification (`vireon-api`)

VIREON includes a production FastAPI server (`vireon_api/main.py`) providing high-throughput HTTP endpoints for remote validation and evidence submission:

### 13.1 `GET /api/v1/health`
- **Response**: `{"status": "healthy", "version": "1.0.0"}`

### 13.2 `GET /api/v1/datasets`
- **Response**: List of available datasets managed by `DatasetManager`.

### 13.3 `POST /api/v1/evidence/register`
- **Request Body**: `EvidenceBundle` JSON schema.
- **Response**: `{"status": "registered", "bundle_id": "..."}`

### 13.4 `GET /api/v1/evidence/verify/{evidence_hash}`
- **Response**: Cryptographic integrity verification report for the target hash.

---

## 15. Comprehensive Testing Protocols, Coverage Enforcement & CI Grep Gates

The testing strategy in VIREON combines Unit Testing, Property-Based Testing (via `hypothesis`), Integration Testing, Benchmark Verification, and Automated Grep Gates.

### 15.1 Unit Testing & Property-Based Testing with Hypothesis
Property-based testing validates that algorithm invariants hold across thousands of randomly generated inputs bounded by valid physiological ranges.

```python
from hypothesis import given, strategies as st
import numpy as np
from vireon_methods.spectral.vireon_welch import VireonWelch

@given(st.lists(st.floats(min_value=-100.0, max_value=100.0), min_size=256, max_size=1024))
def test_welch_psd_property(signal_list):
    signal = np.array(signal_list)
    welch = VireonWelch(fs=250.0, nperseg=128)
    freqs, psd = welch.compute(signal)
    
    # Invariant 1: PSD values must be strictly non-negative
    assert np.all(psd >= 0.0), "PSD contains negative spectral power density"
    
    # Invariant 2: Frequency vector must be strictly monotonically increasing
    assert np.all(np.diff(freqs) > 0.0), "Frequency vector is not monotonic"
```

### 15.2 Coverage Enforcement Guidelines
VIREON maintains strict coverage thresholds enforced via `pytest-cov`:
- **Core Kernel & Contracts (`vireon-core`)**: $100\%$ Line & Branch Coverage.
- **Signal Processing Methods (`vireon-methods`)**: $\ge 95\%$ Line Coverage.
- **Validation Framework (`vireon-validation`)**: $100\%$ Line Coverage.
- **Evidence Graph Engine (`vireon-evidence`)**: $\ge 90\%$ Line Coverage.

```bash
# Execute test suite with coverage enforcement
pytest --cov=vireon_core --cov=vireon_methods --cov=vireon_validation --cov-report=term-missing
```

### 15.3 CI Grep Gate Verification Checklist
To prevent common anti-patterns or hardcoded metrics from entering the codebase, developers must execute all grep gate commands prior to submitting a Pull Request:

1. **Gate 1 (No hardcoded evidence hashes)**:
   ```bash
   ! rg 'evidence_hash\s*=\s*""' vireon-validation/ vireon-core/
   ```
2. **Gate 2 (No synthetic data stubs in production paths)**:
   ```bash
   ! rg "PARQUET_STUB_DATA" vireon-validation/
   ```
3. **Gate 3 (No unseeded numpy randomness)**:
   ```bash
   ! rg "np\.random\.(normal|uniform|choice)" vireon-validation/vireon_validation/perturbations/
   ```
4. **Gate 4 (No fabricated metric counters)**:
   ```bash
   ! rg "failures_logged.*int\(total_runs" vireon-validation/
   ```

---

## 16. Full Monorepo Directory Index & Module Responsibility Matrix

Below is the complete file directory layout of the VIREON monorepo and the exact engineering responsibilities assigned to each subpackage:

| Directory Path | Primary Language / Framework | Engineering Responsibility & Scope | Maintainer Contact |
|---|---|---|---|
| `vireon-core/` | Python 3.11+ / Pydantic | Abstract base interfaces (`ISignal`), Pydantic contract schemas (`EvidenceBundle`), `DeterministicRNG` runtime, plugin registries. | Core Kernel Team |
| `vireon-models/` | Python / NumPy | Array validators, 1D/2D/3D signal wrappers, metadata headers, and sampling rate validators. | Data Systems Team |
| `vireon-methods/` | Python / SciPy / NumPy | Signal processing algorithms across 6 domains (spectral, spatial, connectivity, source localization, time-frequency, deep learning). | Algorithm Team |
| `vireon-validation/` | Python / SciPy | Statistical concordance engines (Lin's CCC, ICC(3,1)), perturbation matrix runners, and reference standard cross-validators. | QA & Compliance |
| `vireon-evidence/` | Python / SQLite / JSON-LD | Cryptographic SHA-256 evidence graph database, registry persistence, LaTeX / Markdown / HTML report generators. | Evidence Systems |
| `vireon-knowledge/` | Python / YAML | Literature citation metadata, paper reproduction manifests, DOI indexing, and domain knowledge graphs. | Science Team |
| `vireon-corpus/` | Python / EDFIO | Open dataset downloader (`DatasetManager`), local disk caching (`~/.vireon/datasets/`), and SHA-256 integrity validators. | Data Systems Team |
| `vireon-lab/` | Python | Research experimentation scripts, hyperparameter tuning runners, and multi-dataset benchmarks. | Research Team |
| `vireon-api/` | Python / FastAPI | Microservice REST API endpoints, OpenAPI documentation generators, and remote evidence submission receivers. | Infrastructure Team |
| `vireon-verification/` | Python / Pytest | 22 literature reproduction test suites, paper verification scripts, and automated regression test harnesses. | QA & Compliance |
| `docs/` | Markdown / MkDocs | Developer manuals, API reference docs, user guides, FDA regulatory binders, and plugin SDK documentation. | Docs & Regulatory |
| `examples/` | Python | 13 standalone runnable example scripts covering real-world BCI, clinical trials, hardware validation, and regulatory submissions. | Developer Rel |
| `scripts/` | Python / Bash | CI verification utilities, literature portfolio generator scripts, document synchronization checkers, and release automation. | DevOps Team |

---

## 17. Sign-Off & Verification

- **Developer Guide**: Complete architecture documentation for VIREON v1.0.0
- **Audited By**: VIREON Core Engineering Team
