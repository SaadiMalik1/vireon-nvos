# vireon-models

`vireon-models` is the engine for Generative Digital Twins. It does not analyze data; it synthesizes it.

## Key Domains
1. **Source Space Models**: Dipole generators mimicking neural circuits (e.g., Thalamocortical loops generating Alpha rhythms).
2. **Forward Models**: Boundary Element Methods (BEM) mapping dipoles to the scalp.
3. **Artifact Generators**: Electrophysiological noise (EOG, EMG, ECG).
4. **Hardware Simulators**: Amplifier noise profiles and telemetry drift.
5. **Disease Models**: Phenomenological statistical models of neurological conditions.

## Current Component Catalog
### Hardware Simulators
- **OpenBCI Cyton** (`hardware.openbci.cyton`): ADS1299 characteristics, 250Hz.
- **Neurosity Crown** (`hardware.neurosity.crown`): 8-channel active electrodes, 256Hz.

### Disease Models
- **Epilepsy** (`disease_model.epilepsy`): High amplitude slow waves coupled with fast spikes.
- **Parkinson's Disease** (`disease_model.parkinsons`): Exaggerated beta-band synchrony in STN.

All models in this repository are adversarial—their purpose is to generate data that breaks algorithms in `vireon-methods`.