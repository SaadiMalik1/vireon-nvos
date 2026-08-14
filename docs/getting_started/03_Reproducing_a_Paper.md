# Reproducing a Paper

One of the largest crises in neurotechnology is the reproducibility of published claims. A research group might state: *"Our modified ICA algorithm achieves 95% SNR improvement in pediatric epilepsy EEG."*

But how does a future laboratory use this safely?

## The Literature Verifier

VIREON utilizes a semantic **Evidence Graph** built on NetworkX. When you attempt to reproduce a paper, VIREON uses the `LiteratureVerifier` to construct a causal map of the original claims.

For example, when running a Campaign, the verifier checks:
1. Did the original paper formally state assumptions regarding artifact distributions?
2. Did the algorithm (`IPlugin`) declare those same mathematical assumptions?
3. Did the output Evidence Bundle deviate statistically from the original paper's baseline metrics?

If the new Evidence Bundle diverges from the historical baseline without a known hardware shift (e.g., CCC drops from 0.90 to 0.65), VIREON flags a **Scientific Regression**.

You no longer have to guess whether you correctly implemented a paper; VIREON mathematically audits your execution against the codified history.
