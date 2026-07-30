# vireon-validation

`vireon-validation` is the automated adversarial testing suite for neurotechnology claims.

## Benchmarks vs. Regression
Unlike `vireon-verification` (which runs CI/CD tests to ensure the code *compiles* and math functions correctly), `vireon-validation` asks scientific questions: "Does this decoder still work if the skin impedance drifts by 20% over 3 hours?"

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

The Execution Engine runs these scenarios iteratively, slowly increasing the `intensity` of the adversarial perturbations (e.g., packet loss, clock jitter, muscle noise) until the target decoder fails. This defines the **Operating Envelope** of the algorithm.