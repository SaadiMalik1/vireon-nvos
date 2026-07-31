# Digital Twins

In VIREON, a Digital Twin is an executable `IPlugin` that generates synthetic data mirroring a specific physical or biological entity.

## Biological Twins
A biological twin models physiological phenomena to stress-test spatial and spectral assumptions:
- **Ocular Twin:** Generates Electrooculography (EOG) artifacts based on Poisson-distributed blink timing.
- **Cortical Twin:** Generates alpha rhythms based on thalamocortical loop dynamics.

## Hardware Twins
To support full-system validation, the hardware digital twin suite goes beyond basic simulation and enforces strict physical boundaries:
- **AmplifierTwin**: Simulates thermal noise scaling relative to impedance mismatches, and applies strict saturation clipping boundaries.
- **TelemetryTwin**: Simulates wireless packet loss (burst dropouts) and sampling jitter (Gaussian phase noise).
- **BatteryDegradationTwin**: Models baseline drift resulting from voltage drops at low charge percentages.

By combining these twins, researchers can test a decoder against a highly realistic, albeit adversarial, simulation of a patient wearing a specific headset, mapping directly to regulatory device profiles.

## Phase E Implementation Status
> [!NOTE]
> As of Phase E, the architecture has expanded to include Massive Campaigns, Hardware Digital Twins, EvidenceBundle v5 (SRI/Regulatory mapping), and the Reproduce CLI. Features described in this document may be subject to these new workflows. If specific API endpoints, models, or UI components are discussed but missing in the codebase, they are currently [STUBBED] pending Phase F implementation.
