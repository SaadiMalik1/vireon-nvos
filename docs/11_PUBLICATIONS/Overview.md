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


## Phase E Validation Status

> [!NOTE]
> **Status: Complete (v1.2.0)**
>
> This section was previously a stub. It has been filled as part of the v1.2.0 remediation.