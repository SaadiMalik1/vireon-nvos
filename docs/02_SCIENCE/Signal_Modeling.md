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

## Phase E Implementation Status
> [!NOTE]
> As of Phase E, the architecture has expanded to include Massive Campaigns, Hardware Digital Twins, EvidenceBundle v5 (SRI/Regulatory mapping), and the Reproduce CLI. Features described in this document may be subject to these new workflows. If specific API endpoints, models, or UI components are discussed but missing in the codebase, they are currently [STUBBED] pending Phase F implementation.
