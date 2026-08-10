# Signal Modeling

To validate algorithms, we must first mathematically define the signals they process.

## The Additive Noise Model
The standard mathematical formulation for a recorded electrophysiological signal $X(t)$ is:

$$ X(t) = S(t) + A(t) + N(t) $$

Where:
- $S(t)$ is the true neural source signal (e.g., a Motor Rhythm).
- $A(t)$ is structured physiological artifacts (e.g., Ocular blinks, EMG).
- $N(t)$ is unstructured or instrumental noise (e.g., Thermal noise, 50/60Hz Line noise).

## Non-Stationarity
A critical challenge in signal modeling is non-stationarity. Brain states shift (e.g., from awake to drowsy), causing the underlying probability distribution of $S(t)$ to change over time. 
VIREON's generative models (`vireon-models`) allow researchers to explicitly schedule state transitions to test how adaptive decoders handle concept drift.

## Phase E Validation Status

> [!NOTE]
> **Status: Complete (v1.2.0)**
>
> Scientific principles are implemented in vireon-core/contracts/ and vireon-knowledge/.
> Runtime contract enforcement (ADF stationarity test) is production-ready.
> Knowledge graph has 20+ rules covering all major algorithms.