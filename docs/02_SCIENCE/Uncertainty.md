# Bayesian Uncertainty

A deterministic prediction (e.g., "The user intends to move left") is insufficient for clinical or high-risk consumer applications. The system must know when it does not know.

## Modeling Uncertainty
VIREON encourages the use of Bayesian or evidential models that output a probability distribution rather than a point estimate. 

By utilizing the `vireon-validation` adversarial generator to slowly increase the noise floor (e.g., thermal noise in the hardware twin), researchers can measure the *calibration* of their uncertainty models. 
Ideally, as the Signal-to-Noise Ratio (SNR) drops, the decoder's confidence should drop proportionally before its accuracy drops. A model that remains 99% confident while its accuracy drops to chance (50%) is poorly calibrated and clinically unsafe.

## Phase E Implementation Status
> [!NOTE]
> As of Phase E, the architecture has expanded to include Massive Campaigns, Hardware Digital Twins, EvidenceBundle v5 (SRI/Regulatory mapping), and the Reproduce CLI. Features described in this document may be subject to these new workflows. If specific API endpoints, models, or UI components are discussed but missing in the codebase, they are currently [STUBBED] pending Phase F implementation.
