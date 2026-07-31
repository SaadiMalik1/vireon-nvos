# vireon-validation

`vireon-validation` is the automated adversarial testing suite for neurotechnology claims. It asks scientific questions: "Does this decoder still work if the skin impedance drifts by 20% over 3 hours?"

## Structure
The repository contains YAML scenario definitions.

```yaml
scenario_id: "vk:Scenario:MotorImagery_ImpedanceDrift"
target: "vireon_models.decoder.CSP_LDA"
perturbations:
  - plugin: "vireon_models.artifacts.ImpedanceDrift"
    intensity: 0.2
metrics:
  - accuracy
  - precision
```

## Massive Campaign Orchestrator
- **Status**: [FULLY IMPLEMENTED]
- The Execution Engine runs scenarios iteratively, generating massive multidimensional grids of algorithms vs. perturbations. It successfully sweeps across parameters to define the **Operating Envelope** of the algorithm.

## Statistical Framework
- **Status**: [FULLY IMPLEMENTED]
- The core statistical methods (`vireon_validation.statistics.framework`) are actively used to compute bounds:
  - Bland-Altman Analysis
  - Intraclass Correlation (ICC)
  - Kolmogorov-Smirnov (KS) Test
  - Cohen's d

## Pipeline Validation
- **Status**: [WIP / PARTIALLY IMPLEMENTED]
- While the orchestrator can run End-to-End pipelines, the native validation of complex cyclic graphs and bidirectional workflows is currently stubbed and only supports linear DAGs.