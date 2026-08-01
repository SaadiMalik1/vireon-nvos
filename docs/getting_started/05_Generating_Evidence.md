# Generating Evidence

When VIREON evaluates a method, it doesn't just print an accuracy score. It generates an `EvidenceBundle`.

## The Anatomy of an Evidence Bundle

An `EvidenceBundle` is a cryptographic construct. It binds together:
- **Dataset Provenance**: Which exact version and hash of the dataset was used?
- **Method Provenance**: What were the Scientific Contracts of the algorithms executed?
- **Environmental Fingerprint**: What OS, Python version, and random seeds were present?
- **Multivariate Metrics**: Beyond scalar accuracy, it computes spatial pattern correlations (Cosine), signal-to-distortion ratios (SDR), and covariance metrics (Amari distance).
- **Perturbation States**: Exactly what noise or dropout conditions were active?

## Trust Through Cryptography

Because the bundle contains cryptographic hashes of the input data, output features, and the Scientific Contracts, the Evidence Bundle becomes tamper-evident. 

If a regulatory body (like the FDA) or a peer reviewer needs to verify the performance of a clinical diagnostic algorithm, the Evidence Bundle proves that the exact codebase generated the exact metrics on the exact data.
