# Scientific Principles

The core scientific principle of VIREON is that **mathematical assumptions matter**.

Neurotechnology sits at the intersection of biology (which is highly non-linear, non-stationary, and chaotic) and digital signal processing (which typically assumes linearity, stationarity, and Gaussian noise).

## The Principle of Falsification
VIREON does not exist to prove that a decoder works. It exists to find the exact conditions under which a decoder *fails*. By discovering these failure boundaries computationally, we prevent catastrophic failures in clinical deployment.

## The Principle of Explicit Constraints
If you use Independent Component Analysis (ICA) to remove eye blinks, you are assuming that the blink artifact is statistically independent from the underlying neural signal. If this assumption is false (e.g., if the user blinks reflexively *in response* to a stimulus), the ICA will project neural data into the noise component, destroying the signal.

VIREON forces this assumption to be declared explicitly in the `ScientificContract` so that adversarial datasets can be constructed to test it.