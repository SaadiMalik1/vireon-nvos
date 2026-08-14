# Cryptographic Evidence Flow

When a Cartesian sweep completes, the results are hashed into an `EvidenceBundle`. This JSON-LD bundle contains the cryptographic hash of the execution environment, the method provenance, the reproducibility summary, and the objective statistical metrics (CCC, SDR).

## Implementation Status
In the current research prototype (v0.2.0), the execution model supports authentic biological datasets alongside deterministic synthetic signals, generating EvidenceBundles with cryptographic hashes and verifiable biostatistical metrics. See `docs/STATUS.md` for details.
