# VIREON Governance Model

## 1. Structure
VIREON is managed through a Benevolent Dictator for Life (BDFL) model, supported by a core team of maintainers, and an Independent Scientific Review Board (ISRB).

## 2. The Independent Scientific Review Board (ISRB)
The ISRB acts as a secondary layer of validation. They are responsible for reviewing major structural changes, dataset inclusion, and algorithmic implementations for scientific validity, ensuring the platform does not accrue "scientific debt."

## 3. Contribution Model
Contributions are accepted strictly via Pull Requests. Every PR must:
1. Pass the deterministic execution CI tests.
2. Meet the SRL (Scientific Readiness Level) criteria defined in the plugin contract.
3. Be accompanied by empirical evidence generated from a validation dataset.


## Phase E Implementation Status
> [!NOTE]
> As of Phase E, the architecture has expanded to include Massive Campaigns, Hardware Digital Twins, EvidenceBundle v5 (SRI/Regulatory mapping), and the Reproduce CLI. Features described in this document may be subject to these new workflows. If specific API endpoints, models, or UI components are discussed but missing in the codebase, they are currently [STUBBED] pending Phase F implementation.
