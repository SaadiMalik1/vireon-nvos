# VIREON External Researcher Quickstart Guide

**Goal:** Install, validate, reproduce landmark literature, and generate publication-ready evidence bundles in under 1 hour.

---

## 1. Installation (2 Minutes)

Clone the repository and install VIREON in editable mode:

```bash
git clone https://github.com/SaadiMalik1/vireon-nvos.git
cd vireon-nvos
pip install -e . --break-system-packages
```

Verify installation:

```bash
pytest vireon-api/tests/test_api.py -v
```

---

## 2. Running Full Algorithm Validation Suite (5 Minutes)

Run the automated numerical cross-validation suite against canonical scientific reference libraries (SciPy, MNE-Python, scikit-learn):

```bash
pytest tests/test_algorithm_validation_suite/ -v
```

Generate the authoritative validation report:

```bash
python scripts/generate_algorithm_validation_report.py
```

Inspect the generated Markdown validation report at `reports/algorithm_validation_report.md`.

---

## 3. Reproducing Landmark Literature Claims (10 Minutes)

Run the full literature reproduction suite:

```bash
pytest vireon-verification/literature/ -v
```

Run a specific landmark reproduction in Python:

```python
from vireon_verification.literature.reproduce_ramoser_2000 import reproduce_ramoser_2000

evidence_bundle = reproduce_ramoser_2000()
print(f"Algorithm: {evidence_bundle.algorithm}")
print(f"CCC vs MNE Reference: {evidence_bundle.statistical_agreement['ccc']:.4f}")
print(f"Evidence Hash: {evidence_bundle.evidence_hash}")
```

---

## 4. Querying the Evidence Graph & SQLite Registry (5 Minutes)

```python
from vireon_evidence.registry.core import EvidenceRegistry
from vireon_evidence.doi import EvidenceIdentifier

registry = EvidenceRegistry("evidence_registry.db")
identifier = EvidenceIdentifier()

# Register evidence bundle
registry.register(evidence_bundle)

# Mint DataCite-compliant DOI metadata
doi_meta = identifier.mint_with_metadata(evidence_bundle)
print(f"Assigned DOI: {doi_meta['doi']}")
```

---

## 5. Exporting Publication Artifacts (10 Minutes)

Generate LaTeX manuscripts and Jupyter notebooks automatically from evidence bundles:

```python
from vireon_evidence.exporters.notebook_generator import NotebookGenerator

generator = NotebookGenerator(evidence_bundle)
generator.save("reproduction_workflow.ipynb")
```

Open and execute `reproduction_workflow.ipynb` in Jupyter Notebook.

---

## 6. Launching REST API & Web Dashboard (5 Minutes)

Start the local FastAPI evidence backend:

```bash
uvicorn vireon_api.main:app --reload --port 8000
```

Access:
- **Interactive Dashboard:** `http://localhost:8000/`
- **Health Check:** `http://localhost:8000/api/health`
- **Evidence API:** `http://localhost:8000/api/evidence`
