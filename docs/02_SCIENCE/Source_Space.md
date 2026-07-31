# Source Space vs Sensor Space

When synthesizing EEG/MEG data, a critical architectural decision is where the signal originates.

## Sensor Space Synthesis (The Naive Approach)
Generating a sine wave and adding it directly to the `C3` electrode is computationally cheap. However, it is physiologically impossible. Brain activity does not occur *at* the electrode.

## Source Space Synthesis (The VIREON Approach)
VIREON mandates that all biological activity is generated in a 3D coordinate space inside the head model (the "Source Space"). 

1. **Current Dipoles:** Neural activity is modeled as a primary current dipole $\mathbf{J}^p(\mathbf{r}, t)$.
2. **Volume Conduction:** The electrical potentials propagate through the brain, skull, and scalp. The skull acts as a spatial low-pass filter, significantly blurring the signal.
3. **The Leadfield:** The projection from the 3D source space to the 2D sensor array is calculated using a Forward Model (e.g., Boundary Element Method), resulting in the Leadfield matrix $\mathbf{L}$.

This ensures that spatial filters (like CSP or Beamformers) trained on VIREON data learn physiologically plausible covariance matrices.

## Phase E Implementation Status
> [!NOTE]
> As of Phase E, the architecture has expanded to include Massive Campaigns, Hardware Digital Twins, EvidenceBundle v5 (SRI/Regulatory mapping), and the Reproduce CLI. Features described in this document may be subject to these new workflows. If specific API endpoints, models, or UI components are discussed but missing in the codebase, they are currently [STUBBED] pending Phase F implementation.
