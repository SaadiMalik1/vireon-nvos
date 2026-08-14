# Bayesian Uncertainty

A deterministic prediction (e.g., "The user intends to move left") is insufficient for clinical or high-risk consumer applications. The system must know when it does not know.

## Modeling Uncertainty
VIREON encourages the use of Bayesian or evidential models that output a probability distribution rather than a point estimate. 

By utilizing the `vireon-validation` adversarial generator to slowly increase the noise floor (e.g., thermal noise in the hardware twin), researchers can measure the *calibration* of their uncertainty models. 
Ideally, as the Signal-to-Noise Ratio (SNR) drops, the decoder's confidence should drop proportionally before its accuracy drops. A model that remains 99% confident while its accuracy drops to chance (50%) is poorly calibrated and clinically unsafe.

## Phase E Validation Status

> [!NOTE]
> **Status: Complete (v1.2.0)**
>
> Scientific principles are implemented in vireon-core/contracts/ and vireon-knowledge/.
> Runtime contract enforcement (ADF stationarity test) is production-ready.
> Knowledge graph has 20+ rules covering all major algorithms.