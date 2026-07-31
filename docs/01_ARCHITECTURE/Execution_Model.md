# Execution Model

VIREON utilizes a declarative, capability-based execution model rather than imperative scripts.

## The Problem with Imperative Scripts
Typically, an experiment is hardcoded:
```python
# Bad Pattern
signal = load_data("eeg.edf")
psd = scipy.signal.welch(signal)
plot(psd)
```
This is brittle. If you want to swap `welch` for `multitaper`, you must modify the source code. If you want to run this across 1,000 datasets with different noise profiles, you must write extensive loops and error handling.

## The Capability Router
In VIREON, you declare the *intent* (the goal), and the Execution Model dynamically resolves the DAG.

```yaml
# VIREON Declarative Pipeline (YAML)
goal: "Estimate Spectral Power"
inputs:
  - "vk:Dataset:SyntheticAlpha10Hz"
constraints:
  - max_srl: 3
  - require_assumption: "vk:Assumption:Stationarity"
```

The Kernel reads this YAML, queries the plugin registry for any plugin that `produces` Spectral Power and satisfies the constraints (e.g., the `WelchPSD` plugin), and executes it. 
This Execution Model allows rapid adversarial testing: you can inject an `ElectrodePop` artifact plugin into the DAG purely by altering the YAML manifest, without touching a single line of Python.

## Phase E Implementation Status
> [!NOTE]
> As of Phase E, the architecture has expanded to include Massive Campaigns, Hardware Digital Twins, EvidenceBundle v5 (SRI/Regulatory mapping), and the Reproduce CLI. Features described in this document may be subject to these new workflows. If specific API endpoints, models, or UI components are discussed but missing in the codebase, they are currently [STUBBED] pending Phase F implementation.
