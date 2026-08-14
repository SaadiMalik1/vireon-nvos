# Tutorials

Welcome to the VIREON Tutorials. 

## End-to-End Execution
These guides are designed to take you from a raw dataset to a fully validated `IEvidence` bundle.

### Tutorial 1: Validating Welch PSD
Learn how to use the declarative YAML interface to pass the `SyntheticAlpha10Hz` dataset through the Welch PSD estimator, and observe how injecting a non-stationary artifact triggers a `ScientificContractViolation`.

### Tutorial 2: Adversarial Decoder Testing
Learn how to wrap a simple scikit-learn Linear Discriminant Analysis (LDA) classifier in an `IPlugin` wrapper, and use `vireon-validation` to test its robustness against increasing levels of telemetry packet loss.


## Phase E Validation Status

> [!NOTE]
> **Status: Complete (v1.2.0)**
>
> Tutorials are runnable and tested in CI.
> examples/first_validation/demo.py is the canonical entry point.
> See docs/06_TUTORIALS/quickstart.md for the 5-minute guide.