# vireon-evidence

## Reporting and Exporters

Handles the translation of raw `EvidenceBundles` into human-readable and machine-actionable artifacts. It houses the `MultiFormatReportGenerator`, which produces Markdown reports (with embedded Bland-Altman and Robustness plots), PDFs, and the Reproducibility Summaries required for publication peer review.

## Integration in Phase E
This repository is integrated into the VIREON scientific ecosystem (see docs/STATUS.md for current implementation status). It supports the generation of verifiable EvidenceBundles and contributes directly to the semantic tracking in the Evidence Graph. All methods are dynamically orchestrated through the Cartesian Benchmark Matrix, ensuring reproducibility and cryptographically assured provenance.
