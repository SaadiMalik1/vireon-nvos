# The Scientific Pipeline

The VIREON scientific pipeline operates via a Cartesian Benchmark Matrix. A dataset (e.g., PhysioNet EEG) is combined with an algorithmic Scientific Contract (e.g., CSP). The matrix injects orthogonal perturbations (white noise, channel drop-out) to plot the algorithmic performance decay, generating a multi-dimensional robustness curve.

## Implementation Status
In the current research prototype (v0.2.0), the execution model supports authentic biological datasets alongside deterministic synthetic signals, generating EvidenceBundles with cryptographic hashes and verifiable biostatistical metrics. See `docs/STATUS.md` for details.
