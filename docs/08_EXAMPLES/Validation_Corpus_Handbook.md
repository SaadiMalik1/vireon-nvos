# Validation Corpus Handbook

VIREON's credibility rests entirely on its Validation Corpus. This handbook details the standardized empirical and synthetic benchmarks used to falsify algorithmic claims.

## Synthetic 10Hz Alpha Oscillation
**ID:** `vk:Dataset:SyntheticAlpha10Hz`
**Purpose:** Verify numerical agreement of basic PSD estimators against standard DSP libraries without confounding biological noise.
- **Ground Truth:** Deterministic sine wave exactly at 10.0Hz, amplitude 1.0.
- **Artifacts:** 50Hz Line Noise, Gaussian White Noise (SNR: 6.02 dB).
- **Benchmark:** `validate_welch.py`
- **Expected Output:** RMSE < 1e-10 against `scipy.signal.welch`.

## MNE Sample Dataset Projection
**ID:** `vk:Dataset:MneSampleForward`
**Purpose:** Verify the structural integrity of the Boundary Element Method (BEM) leadfield projection.
- **Ground Truth:** Known dipole locations in the MNE sample dataset.
- **Artifacts:** None (pure structural projection).
- **Scientific Assumptions:** Linear superposition, Maxwell's quasi-static approximation.
- **Expected Output:** Geometric mean spatial error < 2mm against canonical FreeSurfer/MNE solutions.

*Note: All empirical datasets must declare their acquisition hardware, montage, and subject demographics per the VIREON strict provenance requirements.*


## Phase E Validation Status

> [!NOTE]
> **Status: Complete (v1.2.0)**
>
> This section was previously a stub. It has been filled as part of the v1.2.0 remediation.