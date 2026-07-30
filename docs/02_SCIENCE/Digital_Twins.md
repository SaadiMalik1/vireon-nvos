# Digital Twins

In VIREON, a Digital Twin is an executable `IPlugin` that generates synthetic data mirroring a specific physical or biological entity.

## Hardware Twins
A hardware twin models the signal acquisition chain.
- **Amplifier Noise:** Models the specific thermal noise floor and $1/f$ noise characteristics of a specific ADC (e.g., Texas Instruments ADS1299).
- **Impedance:** Models the skin-electrode interface.
- **Telemetry:** Models packet loss or jitter in Bluetooth/WiFi transmission.

## Biological Twins
A biological twin models physiological phenomena.
- **Ocular Twin:** Generates Electrooculography (EOG) artifacts based on Poisson-distributed blink timing.
- **Cortical Twin:** Generates alpha rhythms based on thalamocortical loop dynamics.

By combining these twins, researchers can test a decoder against a highly realistic, albeit adversarial, simulation of a patient wearing a specific headset.