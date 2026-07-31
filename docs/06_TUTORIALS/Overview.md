# Tutorials

Welcome to the VIREON Tutorials. 

## End-to-End Execution
These guides are designed to take you from a raw dataset to a fully validated `IEvidence` bundle.

### Tutorial 1: Validating Welch PSD
Learn how to use the declarative YAML interface to pass the `SyntheticAlpha10Hz` dataset through the Welch PSD estimator, and observe how injecting a non-stationary artifact triggers a `ScientificContractViolation`.

### Tutorial 2: Adversarial Decoder Testing
Learn how to wrap a simple scikit-learn Linear Discriminant Analysis (LDA) classifier in an `IPlugin` wrapper, and use `vireon-validation` to test its robustness against increasing levels of telemetry packet loss.


## Phase E Implementation Status
> [!NOTE]
> As of Phase E, the architecture has expanded to include Massive Campaigns, Hardware Digital Twins, EvidenceBundle v5 (SRI/Regulatory mapping), and the Reproduce CLI. Features described in this document may be subject to these new workflows. If specific API endpoints, models, or UI components are discussed but missing in the codebase, they are currently [STUBBED] pending Phase F implementation.
