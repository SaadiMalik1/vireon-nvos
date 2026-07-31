# Evidence Quality

The output of a VIREON execution is an `IEvidence` bundle. The quality of this evidence is paramount for community trust and regulatory submission.

## Evidence Bundle v5
The latest standard for evidence serialization (v5) ensures full scientific traceability and regulatory mapping. Features include:
- **Cryptographic Provenance**: Hashing of Git states, dataset BIDS versions, and plugin versions.
- **Hardware & Workflow Logging**: Capturing exactly which hardware twins and end-to-end workflows were executed.

## Regulatory Grade Evidence (SRL-9)
For an `IEvidence` bundle to be submitted to a regulatory body (e.g., FDA), it must:
1. Be cryptographically signed by the Evidence Engine.
2. Rely strictly on `IPlugin` nodes that have achieved at least SRL-5 (Empirical Validation).
3. Demonstrate robust calibration of Bayesian Uncertainty.
4. Supply a fully reproducible JSON-LD graph linking every assumption to peer-reviewed literature in the `vireon-knowledge` graph.

### Regulatory Profiles & SRI
In v5, bundles explicitly map validations directly to standards:
- **FDA GMLP** (Good Machine Learning Practice)
- **IEC 62304** (Medical device software lifecycle)
- **ISO 14971** (Risk management)
- **IEC 60601** (Basic safety)

Additionally, bundles are scored using the **Scientific Reproducibility Index (SRI)**, which allows researchers to instantly gauge the deterministic reliability and cross-platform consistency of the generated evidence.

## Phase E Implementation Status
> [!NOTE]
> As of Phase E, the architecture has expanded to include Massive Campaigns, Hardware Digital Twins, EvidenceBundle v5 (SRI/Regulatory mapping), and the Reproduce CLI. Features described in this document may be subject to these new workflows. If specific API endpoints, models, or UI components are discussed but missing in the codebase, they are currently [STUBBED] pending Phase F implementation.
