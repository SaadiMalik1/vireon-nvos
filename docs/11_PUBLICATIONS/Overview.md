# Reproducible Publications

The ultimate proof of the VIREON ecosystem is the ability to instantly reproduce published scientific findings.

## The Evidence Graph
When a paper is published using VIREON, the authors submit an `IEvidence` JSON-LD bundle to this repository. This bundle contains the exact Git hashes, random seeds, and DAG topology used to generate their results.

## Reproducing a Paper
To reproduce a finding, you do not need to download their scripts or configure their environment. You simply run:
```bash
vireon reproduce vk:Publication:Author2026
```
The Core Engine will parse the bundle, dynamically fetch the exact versions of the plugins, download the fingerprinted dataset from `vireon-corpus`, execute the DAG, and output a boolean confirming whether the generated metrics match the published metrics.


## Phase E Implementation Status
> [!NOTE]
> As of Phase E, the architecture has expanded to include Massive Campaigns, Hardware Digital Twins, EvidenceBundle v5 (SRI/Regulatory mapping), and the Reproduce CLI. Features described in this document may be subject to these new workflows. If specific API endpoints, models, or UI components are discussed but missing in the codebase, they are currently [STUBBED] pending Phase F implementation.
