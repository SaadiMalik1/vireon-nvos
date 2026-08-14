# Scientific Contracts & Plugins

Algorithms in VIREON are not just functions; they are `IPlugin` modules bound to a Scientific Contract. They explicitly declare their physiological and mathematical assumptions (e.g., stationary covariance, linear mixing). If a dataset violates these assumptions, the engine will mathematically isolate the failure mode.

## Implementation Status
In the current research prototype (v0.2.0), the execution model supports authentic biological datasets alongside deterministic synthetic signals, generating EvidenceBundles with cryptographic hashes and verifiable biostatistical metrics. See `docs/STATUS.md` for details.
