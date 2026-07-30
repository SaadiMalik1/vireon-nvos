# vireon-corpus

`vireon-corpus` is the canonical store for empirical validation datasets.

## Requirements for Inclusion
A dataset cannot be added to `vireon-corpus` simply by uploading a CSV. It must be accompanied by:
- A JSON manifest declaring the specific amplifier hardware used.
- The precise spatial coordinates of the electrode montage.
- The cryptographic hash (`sha256`) of the raw files to ensure immutable provenance tracking during Evidence Generation.