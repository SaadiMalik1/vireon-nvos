# vireon-models

`vireon-models` is the engine for Generative Digital Twins. It does not analyze data; it synthesizes it.

## Key Domains
1. **Source Space Models**: Dipole generators mimicking neural circuits.
2. **Forward Models**: Boundary Element Methods (BEM) mapping dipoles to the scalp.
3. **Artifact Generators**: Electrophysiological noise (EOG, EMG, ECG).
4. **Hardware Simulators**: Amplifier noise profiles and telemetry drift.
5. **Disease Models**: Phenomenological statistical models of neurological conditions.

## Current Component Catalog

### Hardware Simulators (Phase E)
- **AmplifierTwin**: [FULLY IMPLEMENTED] Simulates thermal noise and symmetric/asymmetric clipping limits.
- **TelemetryTwin**: [FULLY IMPLEMENTED] Simulates dropped packets (burst loss) and sampling clock jitter.
- **BatteryDegradationTwin**: [FULLY IMPLEMENTED] Simulates baseline drift as power depletes.
- **Specific Hardware Profiles** (e.g., OpenBCI Cyton, Neurosity Crown): [STUBBED] The base classes work, but the exact calibration values for commercial arrays are placeholders pending manufacturer specification integration.

### Disease Models
- **Epilepsy** (`disease_model.epilepsy`): [STUBBED] High amplitude slow waves coupled with fast spikes.
- **Parkinson's Disease** (`disease_model.parkinsons`): [STUBBED] Exaggerated beta-band synchrony in STN.

All models in this repository are adversarial—their purpose is to generate data that breaks algorithms in `vireon-methods`.