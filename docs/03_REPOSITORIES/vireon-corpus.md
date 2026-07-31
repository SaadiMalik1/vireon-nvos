# vireon-corpus

`vireon-corpus` is the canonical store for empirical validation datasets.

## Requirements for Ingestion
To be ingested into `vireon-corpus`, a dataset must:
1. Be structured in BIDS (Brain Imaging Data Structure) format.
2. Have explicit provenance (DOI of original publication).
3. Be hashed cryptographically so the Evidence Engine can lock executions to specific dataset versions.

## Status
- **BIDS Ingestion**: [FULLY IMPLEMENTED] - Datasets can be parsed and hashed.
- **Dataset Integration**: [PARTIALLY IMPLEMENTED] - Specific datasets like `EEGBCI`, `PhysioNet MI`, and `CHB-MIT` are mapped in the ontology, but the automated fetching engine is [STUBBED]. Currently requires manual local downloads.