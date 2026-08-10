# Plugin SDK Guide

VIREON's capability-based architecture allows researchers to integrate new algorithms, hardware models, or datasets without touching the core engine. This is accomplished by implementing the `IPlugin` interface.

## 1. The Anatomy of a Plugin

Every plugin in VIREON must implement `vireon_core.contracts.plugin.IPlugin`.

You do not need to read the kernel source code to build a plugin. You only need to fulfill the contract.

### Step 1: Define the Capabilities
Your plugin must declare what it can do. The kernel routes data based on these capabilities.
```python
@property
def capabilities(self) -> List[PluginCapability]:
    return [PluginCapability(
        id="spectral_estimation",
        version="1.0.0",
        consumes=["ISignal"],
        produces=["ISignal"],
        assumptions=["Finite energy"],
        uncertainty_model=["Variance reduction by K"]
    )]
```

### Step 2: The Scientific Contract
This is the most critical step. You must explicitly declare the mathematical and physiological boundaries of your plugin.

```python
@property
def contract(self) -> ScientificContract:
    return ScientificContract(
        purpose="Estimate PSD via Welch's Method",
        mathematical_assumptions=["Wide-Sense Stationarity", "Ergodicity"],
        supported_modalities=[SignalType.EEG, SignalType.ECOG],
        failure_conditions=["Sampling rate < 10Hz"],
        validation_papers=["10.1109/TAU.1967.1161901"]
    )
```
*Note: If your plugin is fed an `ISignal` that violates these assumptions (e.g., an `ISpike` train instead of `EEG`), the Evidence Engine will flag a contract violation.*

### Step 3: Implement `execute`
The execute method receives heavily-typed `IScientificObject` payloads (e.g., `ISignal`, `IMeasurement`).

```python
def execute(self, inputs: Dict[str, IScientificObject]) -> Dict[str, IScientificObject]:
    signal = inputs.get("signal")
    # Perform mathematical operation on signal.data
    # Wrap result in an IScientificObject
    return {"result": ISignal(sampling_rate=signal.sampling_rate, data=new_data)}
```

## 2. Registering the Plugin
Once implemented, the plugin does not need to be hardcoded into `vireon-core`. The core execution orchestrator uses Python's reflection (or entry points) to discover available plugins in your environment.


## Phase E Validation Status

> [!NOTE]
> **Status: Complete (v1.2.0)**
>
> This section was previously a stub. It has been filled as part of the v1.2.0 remediation.