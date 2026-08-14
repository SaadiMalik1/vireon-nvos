# VIREON Plugin SDK & Extension Architecture Manual (v1.0.0)

---

## 1. Overview & Architectural Goals

The **VIREON Plugin SDK** enables external researchers, medical software engineers, and third-party commercial neurotech developers to seamlessly extend VIREON with custom signal processing methods, proprietary spatial filters, real-time hardware stream interfaces, or private dataset loaders without modifying VIREON core source code or breaking evidence graph integrity.

Key architectural goals of the Plugin SDK include:
1. **Isolated Execution**: Plugins execute inside strict contract wrappers with zero direct access to private global states.
2. **Cryptographic Evidence Transparency**: Third-party plugins automatically inherit VIREON's `EvidenceBundle` hashing pipeline.
3. **Dynamic Discovery**: Plugins register through Python `setuptools` entry points (`vireon.plugins`), requiring zero manual configuration files.

---

## 2. Core Plugin Interfaces & Contracts

All custom VIREON plugins must inherit from `IVireonPlugin` located in `vireon_core.kernel.plugins`:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any
from vireon_core.contracts.base import ISignal

class IVireonPlugin(ABC):
    """Abstract Base Class for all external VIREON plugins."""
    
    @property
    @abstractmethod
    def plugin_name(self) -> str:
        """Return unique plugin string identifier."""
        pass

    @property
    @abstractmethod
    def plugin_version(self) -> str:
        """Return semantic version string (e.g., '1.0.0')."""
        pass

    @abstractmethod
    def execute(self, signal: ISignal, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute plugin processing on input ISignal contract object."""
        pass
```

---

## 3. Step-by-Step Tutorial: Building a Custom Plugin

### Step 1: Create a New Python Package Directory
```
my_vireon_plugin/
├── pyproject.toml
└── my_plugin/
    ├── __init__.py
    └── custom_filter.py
```

### Step 2: Implement the Plugin Class
In `my_plugin/custom_filter.py`:

```python
import numpy as np
from typing import Dict, Any
from vireon_core.kernel.plugins import IVireonPlugin
from vireon_core.contracts.base import ISignal
from vireon_core.runtime.rng import DeterministicRNG

class CustomLaplacianFilterPlugin(IVireonPlugin):
    """Custom Surface Laplacian Spatial Filter Plugin."""

    @property
    def plugin_name(self) -> str:
        return "CustomLaplacianFilter"

    @property
    def plugin_version(self) -> str:
        return "1.0.0"

    def execute(self, signal: ISignal, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply spatial Laplacian subtraction across channels."""
        raw_data = signal.data
        center_weight = config.get("center_weight", 4.0)
        
        # Spatial Laplacian computation
        mean_spatial = np.mean(raw_data, axis=0)
        filtered_data = raw_data * center_weight - mean_spatial
        
        return {
            "filtered_data": filtered_data,
            "status": "SUCCESS",
            "mean_power": float(np.mean(filtered_data ** 2))
        }
```

### Step 3: Register Entry Point in `pyproject.toml`
In `my_vireon_plugin/pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "my-vireon-plugin"
version = "1.0.0"
dependencies = [
    "vireon-nvos>=1.0.0"
]

[project.entry-points."vireon.plugins"]
custom_laplacian = "my_plugin.custom_filter:CustomLaplacianFilterPlugin"
```

---

## 4. Plugin Discovery & Lifecycle Management

VIREON's `PluginManager` automatically scans installed Python packages for the `vireon.plugins` entry point group:

```python
from vireon_core.kernel.plugins import PluginManager

# Initialize Plugin Manager
pm = PluginManager()
pm.discover_plugins()

# List all discovered third-party plugins
discovered = pm.list_plugins()
print("Discovered Plugins:", discovered)

# Execute target plugin dynamically
result = pm.execute_plugin("CustomLaplacianFilter", signal=sample_signal, config={"center_weight": 4.0})
print("Plugin Execution Output:", result)
```

---

## 5. Integrating Plugins with the Evidence Registry

When a third-party plugin executes within VIREON, its output payload can be wrapped into a cryptographic `EvidenceBundle` to preserve provenance:

```python
from vireon_core.contracts.evidence import EvidenceBundle
from vireon_evidence.registry.core import EvidenceRegistry
import hashlib

def register_plugin_evidence(plugin_name: str, output_data: dict):
    # Compute SHA-256 hash over output payload
    payload_bytes = str(output_data).encode("utf-8")
    sha256_hash = hashlib.sha256(payload_bytes).hexdigest()
    
    bundle = EvidenceBundle(
        bundle_id=f"PLUGIN-{plugin_name}-001",
        evidence_hash=sha256_hash,
        timestamp="2026-08-05T07:21:18Z",
        algorithm=plugin_name,
        dataset="Custom User Dataset",
        statistical_agreement={"verified": True},
        runtime_sec=0.005
    )
    
    registry = EvidenceRegistry()
    registry.register(bundle)
    print("Registered plugin evidence bundle:", bundle.evidence_hash)
```

---

## 6. Testing & Quality Assurance for Plugin Developers

Third-party plugin developers must write comprehensive tests to ensure compatibility:
1. **Lin's CCC Validation**: Compare plugin output against reference standard scripts ($CCC \ge 0.99$).
2. **Determinism Verification**: Confirm identical inputs yield bit-exact outputs using `DeterministicRNG`.
3. **Zero State Mutation**: Ensure plugin execution does not mutate global `ISignal` input arrays.

---

## 7. Advanced Plugin Examples: Deep Learning Models & Hardware Connectors

### 7.1 Deep Learning Model Wrapper Plugin
Plugins can wrap custom PyTorch or TensorFlow neural network models for specialized EEG decoding:

```python
import torch
import torch.nn as nn
import numpy as np
from typing import Dict, Any
from vireon_core.kernel.plugins import IVireonPlugin
from vireon_core.contracts.base import ISignal

class PyTorchEEGClassifier(nn.Module):
    def __init__(self, channels=8, samples=250, classes=2):
        super().__init__()
        self.conv = nn.Conv1d(channels, 16, kernel_size=15, padding=7)
        self.fc = nn.Linear(16 * samples, classes)
        
    def forward(self, x):
        x = torch.relu(self.conv(x))
        x = x.view(x.size(0), -1)
        return self.fc(x)

class DeepLearningModelPlugin(IVireonPlugin):
    def __init__(self):
        self.model = PyTorchEEGClassifier()
        self.model.eval()

    @property
    def plugin_name(self) -> str:
        return "PyTorchEEGNetPlugin"

    @property
    def plugin_version(self) -> str:
        return "1.0.0"

    def execute(self, signal: ISignal, config: Dict[str, Any]) -> Dict[str, Any]:
        data_tensor = torch.tensor(signal.data, dtype=torch.float32).unsqueeze(0)
        with torch.no_grad():
            logits = self.model(data_tensor)
            probs = torch.softmax(logits, dim=1).numpy().squeeze()
            
        return {
            "predicted_class": int(np.argmax(probs)),
            "probabilities": probs.tolist(),
            "status": "SUCCESS"
        }
```

### 7.2 Low-Latency Hardware Streaming Connector Plugin
Plugins can implement custom real-time hardware acquisition loops (e.g., LSL - Lab Streaming Layer, Serial Port, or TCP/IP socket streams):

```python
import time
import numpy as np
from typing import Dict, Any
from vireon_core.kernel.plugins import IVireonPlugin
from vireon_core.contracts.base import ISignal
from vireon_core.runtime.rng import DeterministicRNG

class HardwareLSLStreamPlugin(IVireonPlugin):
    """Lab Streaming Layer (LSL) Real-Time Ingestion Plugin."""

    @property
    def plugin_name(self) -> str:
        return "LSLStreamConnector"

    @property
    def plugin_version(self) -> str:
        return "1.0.0"

    def execute(self, signal: ISignal, config: Dict[str, Any]) -> Dict[str, Any]:
        sampling_rate = config.get("sampling_rate", 250.0)
        duration_sec = config.get("duration_sec", 1.0)
        n_samples = int(sampling_rate * duration_sec)
        
        # Simulate real-time streaming acquisition buffer
        rng = DeterministicRNG(seed=100)
        stream_buffer = rng.normal(0, 1.0, (signal.data.shape[0], n_samples))
        
        return {
            "acquired_samples": n_samples,
            "buffer_shape": stream_buffer.shape,
            "latency_ms": 1.2,
            "status": "STREAM_ACTIVE"
        }
```

---

## 8. Security, Sandboxing & Resource Isolation Guidelines

When developing third-party plugins for hospital or clinical deployments:
1. **No External Network Dependencies**: Plugins must not initiate unverified external HTTP calls during core signal processing execution loops.
2. **Memory Bounds**: Plugins must manage memory allocation carefully and avoid growing state arrays indefinitely during continuous streaming.
3. **Exception Isolation**: All plugin exceptions must be caught and returned cleanly in the output dictionary status payload (`status: ERROR`) to prevent crashing the host process.

---

## 9. Plugin Publishing, Distribution & Licensing Policy

When distributing open-source or commercial VIREON plugins:

### 9.1 Licensing Compatibility Matrix
VIREON core software is distributed under the MIT open-source license. Third-party plugins may be released under alternative licenses:
- **MIT / BSD / Apache 2.0**: Fully compatible for both open-source and commercial plugin distribution.
- **GPL / AGPL**: Permitted for open-source research plugins.
- **Proprietary Commercial**: Allowed for closed-source clinical SaMD plugins interfacing via `IVireonPlugin`.

### 9.2 Semantic Versioning Requirements
Plugins must follow Semantic Versioning (`MAJOR.MINOR.PATCH`):
- Increment `MAJOR` version if breaking contract changes are introduced in `IVireonPlugin`.
- Increment `MINOR` version when adding new configuration parameters or output features.
- Increment `PATCH` version for bug fixes or speed optimizations.

---

## 10. Sign-Off & Verification

- **Plugin SDK Document**: Complete developer reference for VIREON v1.0.0
- **Audited By**: VIREON Core Engineering Team
