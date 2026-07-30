# vireon-corpus

`vireon-corpus` is the canonical store for empirical validation datasets.

## Requirements for Inclusion
A dataset cannot be added to `vireon-corpus` simply by uploading a CSV. It must be accompanied by:
- A JSON/YAML manifest declaring the specific amplifier hardware used.
- The precise spatial coordinates of the electrode montage.
- The cryptographic hash (`sha256`) of the raw files to ensure immutable provenance tracking during Evidence Generation.

## Current Dataset Catalog
- **CHB-MIT** (`dataset.chb_mit`): EEG recordings from pediatric subjects with intractable seizures.
- **MNE Sample** (`dataset.mne_sample`): MEG/EEG data from a single subject presenting audiovisual stimuli.
- **BCI Competition IV 2a** (`dataset.bci_competition_iv_2a`): 4-class motor imagery EEG dataset.