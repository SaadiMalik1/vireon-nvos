# VIREON NVOS
**Neurotechnology Validation Operating System**

[![Documentation Status](https://img.shields.io/badge/docs-latest-blue.svg)](https://github.com/SaadiMalik1/vireon-nvos)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

VIREON is an open scientific infrastructure designed for reproducible neurotechnology validation, digital twins, evidence generation, and independent verification. 

Unlike traditional "simulation" frameworks, VIREON intentionally generates *Adversarial Digital Twins* to stress-test decoders, hardware models, and artifact generators under mathematically bounded constraints.

## 🚀 The Paradigm: Validation, Not Simulation

Traditional black-box decoders often fail to generalize to real-world environments because validation datasets lack realistic artifacts (e.g., telemetry packet loss, electrode pops). 

VIREON abstracts the complexities of experimental neurophysiology into a **capability-based kernel**. 
- **Scientific Contracts**: Every plugin explicitly declares its mathematical, statistical, and physiological assumptions. If data violates these assumptions (e.g., applying stationary methods to transient event-related potentials), the kernel halts.
- **Evidence Engine**: Instead of just producing numerical results, VIREON produces immutable `IEvidence` JSON-LD bundles. It tracks provenance, random seeds, and exact Git hashes to solve the reproducibility crisis.

## 📦 Installation

To install the VIREON NVOS core framework and all standard modules for local development:

```bash
git clone https://github.com/SaadiMalik1/vireon-nvos.git
cd vireon-nvos
pip install -e .
```

Note: The frontend GUI is currently deferred to a future release; VIREON NVOS is operated via its CLI and Python APIs.

## 📚 Documentation Ecosystem

The core value of VIREON is its rigorous documentation and ontological definitions. The documentation is treated as a first-class citizen and built via MkDocs.

To read the comprehensive Whitepaper, Architecture Book, Scientific Manual, and Contributor Guides locally:

```bash
# Install dependencies
pip install mkdocs-material pymdown-extensions mkdocstrings[python]

# Serve the documentation locally
mkdocs serve
```

## 🏗️ Repository Ecosystem
- **`vireon-core`**: The capability-based kernel, execution DAG, and Evidence Engine.
- **`vireon-knowledge`**: The formal ontology and Knowledge Graph linking methods, assumptions, and literature.
- **`vireon-models`**: Generative digital twins (Artifacts, Hardware simulators, Head models, Source space).
- **`vireon-methods`**: Signal processing and statistical methodologies.
- **`vireon-validation`**: Automated benchmarking scenarios and execution harnesses.
- **`vireon-verification`**: Continuous Integration checks ensuring standard mathematical and numerical agreements.
- **`vireon-corpus`**: High-quality, curated, and fingerprinted physiological datasets.
- **`vireon-publications`**: Executable evidence graphs reproducing the findings of canonical papers.

## 🤝 Contributing
VIREON adheres to strict Scientific Readiness Levels (SRL) ranging from 0 to 9. We prioritize scientific rigor over velocity. All new plugins must supply an explicit `ScientificContract` mapping their assumptions to the Knowledge Graph. 

Please see the [Contributor Guide](docs/13_CONTRIBUTING/Contributor_Guide.md) in the documentation site for more information.

## 📝 License
This project is licensed under the MIT License.
