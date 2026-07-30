# Repository Map

The VIREON ecosystem is intentionally fragmented into domain-specific repositories to enforce decoupling.

## The Kernel
- **`vireon-core`**: The execution DAG, capability router, and Evidence Engine. Contains no scientific logic.

## The Ontology
- **`vireon-knowledge`**: The JSON-LD Knowledge Graph mapping methods, assumptions, and hardware characteristics.

## The Science
- **`vireon-models`**: Generative digital twins. Source space dipoles, hardware amplifiers, artifact synthesizers.
- **`vireon-methods`**: Signal processing and statistical algorithms (e.g., Welch PSD, CSP, ICA).

## Validation & Testing
- **`vireon-validation`**: Automated scenario manifests for adversarial testing of decoders.
- **`vireon-verification`**: CI/CD regression tests ensuring numerical equivalence (SRL-3) of the methods.

## Data & Evidence
- **`vireon-corpus`**: Highly curated, fingerprinted physiological datasets (e.g., MNE Sample, PhysioNet).
- **`vireon-publications`**: Executable JSON-LD evidence bundles that reproduce canonical papers.
- **`vireon-reference`**: Ground-truth implementations (often slow, unoptimized Python) used to verify faster rust/C++ extensions.
- **`vireon-lab`**: Interactive Jupyter notebooks and tutorials for exploring the ecosystem.