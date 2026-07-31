# Benchmarking

Benchmarking in VIREON is the automated execution of Validation scenarios to define the operational limits of algorithms.

## Execution
Benchmarks are defined in YAML manifests within `vireon-validation`. They specify:
1. The target plugin (e.g., `WelchPSD`) or End-to-End Workflow (e.g., `Motor Imagery Pipeline`).
2. The empirical dataset or generative digital twin.
3. The expected metric (e.g., `RMSE`, `Cohen's d`).
4. The maximum allowed tolerance (e.g., `1e-6`).

## Massive Factorial Campaigns
In Phase C and beyond, benchmarking is executed via the `MassiveCampaignOrchestrator`. Instead of 1:1 testing, the orchestrator generates a multidimensional factorial grid sweeping across:
- **Algorithms**: e.g., CSP vs ICA vs Multitaper
- **Datasets**: e.g., CHB-MIT, EEGBCI, PhysioNet MI
- **Perturbations**: e.g., 0% to 50% Packet Loss, 0 to 100mV Jitter
- **Hardware Profiles**: e.g., Cyton vs ADS1299
- **Seeds**: Stochastic robustness.

## The Failure Atlas
Failures during massive campaigns are not discarded. They are routed to the `Failure Atlas` (`vireon_evidence.registry.failure_atlas`). This allows the Knowledge Graph to explicitly record the exact boundary conditions where an algorithm ceases to function, transitioning VIREON from just "running benchmarks" to mapping the absolute limits of computational neuroscience.

## Phase E Implementation Status
> [!NOTE]
> As of Phase E, the architecture has expanded to include Massive Campaigns, Hardware Digital Twins, EvidenceBundle v5 (SRI/Regulatory mapping), and the Reproduce CLI. Features described in this document may be subject to these new workflows. If specific API endpoints, models, or UI components are discussed but missing in the codebase, they are currently [STUBBED] pending Phase F implementation.
