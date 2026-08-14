# VIREON Tutorial 01: Quickstart

Welcome to VIREON (Validation, Integrity, Research Engine for Open Neuro Interfaces). This quickstart demonstrates how to run a first algorithm validation and generate a verifiable evidence bundle.

## Installation

```bash
git clone https://github.com/SaadiMalik1/vireon-nvos.git
cd vireon-nvos
pip install -e .
```

## Running the Quickstart Demo

VIREON provides a one-click first validation script that executes an end-to-end benchmark between native algorithms (such as CSP or Welch) and reference packages (such as SciPy or MNE), persisting cryptographic evidence bundles.

```python
import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.machine_learning.csp import CSPPlugin
from vireon_validation.benchmarks.matrix import BenchmarkMatrix

# 1. Initialize Deterministic RNG for scientific reproducibility
rng = DeterministicRNG(seed=42)
n_epochs, n_channels, n_samples = 30, 8, 250
X = rng.normal(0, 1, (n_epochs, n_channels, n_samples))
y = np.array([0, 1] * (n_epochs // 2))

# 2. Add class-discriminable signal
t = np.arange(n_samples) / 250.0
for i in range(n_epochs):
    if y[i] == 0:
        X[i, :4] += 3.0 * np.sin(2 * np.pi * 10.0 * t)
    else:
        X[i, 4:] += 3.0 * np.sin(2 * np.pi * 10.0 * t)

# 3. Create Benchmark Matrix and run
matrix = BenchmarkMatrix(seed=42)
matrix.add_method(CSPPlugin(n_components=2))
matrix.add_dataset("synthetic_motor_imagery", data=X, labels=y)

bundles = matrix.execute_matrix()
print(f"Produced {len(bundles)} evidence bundle(s).")
print(f"Evidence Hash: {bundles[0]['evidence_hash']}")
print(f"Lin's CCC: {bundles[0]['statistical_agreement']['ccc']:.4f}")
print(f"Verdict: {bundles[0]['pass_fail']}")
```

## Inspecting Evidence

Evidence bundles contain:
- Execution hashes sha256
- Statistical concordance metrics (CCC, RMSE, ICC)
- Bootstrap confidence intervals
- DataCite and Schema.org metadata
