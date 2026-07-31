# Interactive Labs

The `vireon-lab` repository contains interactive environments (Jupyter Notebooks and Streamlit apps) for intuitively exploring the boundaries of neurotechnology.

## Available Labs

1. **The Dipole Sandbox:** A 3D interactive viewer plotting the MNE sample brain. Drag a virtual dipole across the motor cortex and watch how the sensor-space projection shifts in real-time based on the Boundary Element Method (BEM) leadfield.
2. **The Artifact Synthesizer:** Play with the parameters of the Ocular Blink generator. Adjust the Poisson lambda rate and observe the spectral leakage effects on a simulated EEG trace.
3. **The Contract Validator:** An interactive graph explorer for `vireon-knowledge`. Input a set of methods and datasets, and the app will visually highlight any conflicting scientific assumptions.


## Phase E Implementation Status
> [!NOTE]
> As of Phase E, the architecture has expanded to include Massive Campaigns, Hardware Digital Twins, EvidenceBundle v5 (SRI/Regulatory mapping), and the Reproduce CLI. Features described in this document may be subject to these new workflows. If specific API endpoints, models, or UI components are discussed but missing in the codebase, they are currently [STUBBED] pending Phase F implementation.
