# VIREON Tutorial 03: Literature Reproduction

Learn how to reproduce published neurotechnology claims using real or canonical datasets and generate peer-review ready evidence bundles.

## Canonical Reproductions in VIREON

VIREON includes canonical reproductions for landmark neuroimaging papers:
- **Welch (1967)**: Averaged periodogram spectral density estimation.
- **Ramoser et al. (2000)**: Optimal spatial filtering for motor imagery classification (CSP).
- **Hyvärinen (2000)**: Independent Component Analysis (FastICA) for artifact rejection.
- **Vinck et al. (2011)**: Weighted Phase Lag Index (WPLI) for volume-conduction invariant connectivity.

## Reproducing Ramoser 2000 CSP on BCI Data

```python
from vireon_verification.literature.reproduce_ramoser_2000 import reproduce_ramoser_2000

evidence_bundle = reproduce_ramoser_2000()
print(f"Algorithm: {evidence_bundle.algorithm}")
print(f"Paper: Ramoser et al. (2000)")
print(f"CCC vs MNE Reference: {evidence_bundle.statistical_agreement['ccc']:.4f}")
print(f"Execution Hash: {evidence_bundle.evidence_hash}")
```

All literature reproductions produce immutable EvidenceBundle structures stored in the SQLite graph and registry.
