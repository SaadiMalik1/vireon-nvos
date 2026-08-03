# Workstream D — Evidence Infrastructure (S19-S23) + Workstream E — Publication Pipeline + API + Docs (S24-S30)

**Goal:** Persistent evidence graph, DOI minting, LaTeX/notebook generators, FastAPI backend, tutorials.

---

## S19: SQLite-Persistent Evidence Graph

**Effort:** M | **Dependencies:** None | **Verification:** G5

### Context
`EvidenceGraph` uses in-memory `networkx.DiGraph`. Evidence is lost on process restart. Need SQLite persistence.

### Implementation

Modify `vireon-evidence/vireon_evidence/graph/core.py`:

```python
import sqlite3
import json
import networkx as nx
from typing import Optional

class EvidenceGraph:
    def __init__(self, db_path: Optional[str] = None):
        self._graph = nx.DiGraph()
        self.db_path = db_path
        if db_path:
            self._init_db()
            self._load_from_db()
    
    def _init_db(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS nodes (
                node_id TEXT PRIMARY KEY,
                node_type TEXT,
                data JSON
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS edges (
                source TEXT,
                target TEXT,
                relation TEXT,
                PRIMARY KEY (source, target, relation)
            )
        """)
        self.conn.commit()
    
    def add_node(self, node):
        self._graph.add_node(node.node_id, data=node.model_dump())
        if self.db_path:
            self.conn.execute(
                "INSERT OR REPLACE INTO nodes VALUES (?, ?, ?)",
                (node.node_id, node.node_type, json.dumps(node.model_dump(), default=str))
            )
            self.conn.commit()
    
    def add_relationship(self, source, target, relation):
        self._graph.add_edge(source, target, relation=relation)
        if self.db_path:
            self.conn.execute(
                "INSERT OR REPLACE INTO edges VALUES (?, ?, ?)",
                (source, target, relation)
            )
            self.conn.commit()
    
    def _load_from_db(self):
        cur = self.conn.execute("SELECT node_id, data FROM nodes")
        for node_id, data_json in cur:
            self._graph.add_node(node_id, data=json.loads(data_json))
        cur = self.conn.execute("SELECT source, target, relation FROM edges")
        for source, target, relation in cur:
            self._graph.add_edge(source, target, relation=relation)
    
    def persist(self):
        """Flush in-memory graph to SQLite."""
        if self.db_path:
            self.conn.commit()
    
    def list_nodes(self):
        return list(self._graph.nodes)
```

### Tests

```python
def test_graph_persists_to_sqlite(tmp_path):
    from vireon_evidence.graph.core import EvidenceGraph
    from vireon_evidence.ontology.nodes import MethodNode
    
    db = str(tmp_path / "test.db")
    g1 = EvidenceGraph(db_path=db)
    g1.add_node(MethodNode(node_id="test", canonical_name="Test", version="1.0"))
    g1.persist()
    
    # New instance loads from DB
    g2 = EvidenceGraph(db_path=db)
    assert "test" in g2.list_nodes()

def test_graph_edges_persist(tmp_path):
    from vireon_evidence.graph.core import EvidenceGraph
    from vireon_evidence.ontology.nodes import MethodNode, DatasetNode
    
    db = str(tmp_path / "test.db")
    g1 = EvidenceGraph(db_path=db)
    g1.add_node(MethodNode(node_id="m1", canonical_name="M", version="1.0"))
    g1.add_node(DatasetNode(node_id="d1", bids_version="1.0", doi=None))
    g1.add_relationship("m1", "d1", "validated_on")
    g1.persist()
    
    g2 = EvidenceGraph(db_path=db)
    assert g2._graph.has_edge("m1", "d1")
```

### Gemini Prompt
```
You are executing task S19. Add SQLite persistence to vireon-evidence/vireon_evidence/graph/core.py. EvidenceGraph accepts db_path param. If provided: init SQLite tables (nodes, edges), auto-load on construction, auto-save on add_node/add_relationship. Add persist() method. Write 2 tests: nodes survive restart, edges survive restart. Branch: svp/S19-sqlite-evidence-graph. TDD. Commit. PR. Stop.
```

---

## S20-S23: Evidence Registry, DOI, Queries, Export Formats (Batched)

### S20: Evidence Registry
```python
# vireon-evidence/vireon_evidence/registry.py
class EvidenceRegistry:
    def __init__(self, db_path: str = "evidence_registry.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("""CREATE TABLE IF NOT EXISTS bundles (
            evidence_hash TEXT PRIMARY KEY, bundle JSON, timestamp TEXT, algorithm TEXT, dataset TEXT
        )""")
    
    def register(self, bundle: EvidenceBundle):
        self.conn.execute("INSERT OR REPLACE INTO bundles VALUES (?,?,?,?,?)",
            (bundle.evidence_hash, bundle.model_dump_json(), bundle.timestamp, bundle.algorithm, bundle.dataset))
        self.conn.commit()
    
    def retrieve(self, evidence_hash: str) -> Optional[EvidenceBundle]:
        cur = self.conn.execute("SELECT bundle FROM bundles WHERE evidence_hash=?", (evidence_hash,))
        row = cur.fetchone()
        if row:
            return EvidenceBundle(**json.loads(row[0]))
        return None
    
    def list_bundles(self, algorithm: str = None, dataset: str = None) -> list:
        query = "SELECT evidence_hash, algorithm, dataset FROM bundles"
        params = []
        if algorithm:
            query += " WHERE algorithm=?"
            params.append(algorithm)
        if dataset:
            query += " WHERE dataset=?" if not algorithm else " AND dataset=?"
            params.append(dataset)
        cur = self.conn.execute(query, params)
        return [{"hash": r[0], "algorithm": r[1], "dataset": r[2]} for r in cur.fetchall()]
```

### S21: DOI Minting
```python
# vireon-evidence/vireon_evidence/doi.py
class DOIMinter:
    def __init__(self, prefix: str = "10.5072/vireon"):  # 10.5072 is a test prefix
        self.prefix = prefix
    
    def mint(self, bundle: EvidenceBundle) -> str:
        """Mint a DOI for an evidence bundle."""
        suffix = bundle.evidence_hash[:16]
        return f"{self.prefix}/{suffix}"
    
    def mint_with_metadata(self, bundle: EvidenceBundle) -> dict:
        doi = self.mint(bundle)
        return {
            "doi": doi,
            "title": f"VIREON Evidence Bundle: {bundle.algorithm} on {bundle.dataset}",
            "creator": "VIREON NVOS",
            "publisher": "VIREON",
            "publication_year": 2025,
            "resource_type": "Dataset",
            "description": f"Evidence bundle with CCC={bundle.statistical_agreement.get('ccc', 'N/A')}",
            "url": f"https://vireon.org/evidence/{bundle.evidence_hash}"
        }
```

### S22: Complex Graph Queries
```python
# Add to vireon-evidence/vireon_evidence/queries/query_engine.py
def query_methods_by_dataset_and_metric(self, dataset_id: str, min_ccc: float = 0.7) -> list:
    """Find all methods validated on a dataset with CCC above threshold."""
    results = []
    for node_id in self.graph._graph.nodes:
        node_data = self.graph._graph.nodes[node_id].get("data", {})
        if node_data.get("node_type") == "EvidenceBundle":
            if node_data.get("dataset") == dataset_id:
                ccc = node_data.get("statistical_agreement", {}).get("ccc", 0)
                if ccc >= min_ccc:
                    results.append({"method": node_data.get("algorithm"), "ccc": ccc, "hash": node_data.get("evidence_hash")})
    return sorted(results, key=lambda x: -x["ccc"])
```

### S23: Evidence Export Formats
```python
# vireon-evidence/vireon_evidence/exporters/format_exporters.py
import json, bibtex

def export_to_jsonld(bundle: EvidenceBundle) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "@id": f"https://vireon.org/evidence/{bundle.evidence_hash}",
        "name": f"VIREON Evidence: {bundle.algorithm}",
        "creator": "VIREON NVOS",
        "datePublished": bundle.timestamp,
        "measurementTechnique": bundle.algorithm,
        "variableMeasured": bundle.statistical_agreement,
    }

def export_to_bibtex(bundle: EvidenceBundle) -> str:
    return f"""@dataset{{{bundle.evidence_hash[:16]},
  title = {{VIREON Evidence: {bundle.algorithm}}},
  author = {{VIREON NVOS}},
  year = {{2025}},
  doi = {{10.5072/vireon/{bundle.evidence_hash[:16]}}},
  url = {{https://vireon.org/evidence/{bundle.evidence_hash}}}
}}"""
```

### Gemini Prompts (batched)
```
S20: Create vireon-evidence/vireon_evidence/registry.py — EvidenceRegistry class with SQLite backend. register(bundle), retrieve(hash), list_bundles(algorithm, dataset). Write 3 tests. Branch: svp/S20-evidence-registry.

S21: Create vireon-evidence/vireon_evidence/doi.py — DOIMinter class. mint(bundle) → DOI string. mint_with_metadata(bundle) → dict with DataCite metadata. Use test prefix 10.5072. Write 2 tests. Branch: svp/S21-doi-minting.

S22: Add query_methods_by_dataset_and_metric to vireon-evidence/vireon_evidence/queries/query_engine.py. Traverses graph, finds EvidenceBundle nodes matching dataset, filters by CCC threshold, returns sorted list. Write 2 tests. Branch: svp/S22-complex-graph-queries.

S23: Create vireon-evidence/vireon_evidence/exporters/format_exporters.py — export_to_jsonld(bundle) → JSON-LD dict, export_to_bibtex(bundle) → BibTeX string. Write 2 tests. Branch: svp/S23-evidence-export-formats.
```

---

## S24: LaTeX Paper Generator

**Effort:** M | **Dependencies:** None | **Verification:** G6

### Implementation

Create `vireon-evidence/vireon_evidence/exporters/latex_generator.py`:

```python
"""Generate a LaTeX paper from an evidence bundle."""
from vireon_core.contracts.evidence import EvidenceBundle
from datetime import datetime

class LaTeXReportGenerator:
    def __init__(self, bundle: EvidenceBundle):
        self.bundle = bundle
    
    def generate(self) -> str:
        b = self.bundle
        ccc = b.statistical_agreement.get("ccc", "N/A")
        rmse = b.statistical_agreement.get("rmse", "N/A")
        
        return f"""\\documentclass[11pt]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{amsmath, amssymb}}
\\usepackage{{graphicx}}
\\usepackage{{hyperref}}
\\usepackage{{booktabs}}
\\usepackage{{geometry}}
\\geometry{{margin=1in}}

\\title{{VIREON Evidence Report: {b.algorithm}}}
\\author{{VIREON NVOS}}
\\date{{{datetime.now().strftime('%B %d, %Y')}}}

\\begin{{document}}
\\maketitle

\\begin{{abstract}}
This report documents the validation of {b.algorithm} on the {b.dataset} dataset.
The evidence bundle hash is \\texttt{{{b.evidence_hash[:32]}...}}.
The concordance correlation coefficient (CCC) between the method under test and
the reference implementation is {ccc:.4f}.
The pass/fail verdict is: \\textbf{{{b.pass_fail}}}.
\\end{{abstract}}

\\section{{Method}}
\\textbf{{Algorithm:}} {b.algorithm}\\\\
\\textbf{{Dataset:}} {b.dataset}\\\\
\\textbf{{Perturbation:}} {b.perturbation}\\\\
\\textbf{{Random Seed:}} {b.random_seed}\\\\
\\textbf{{Runtime:}} {b.runtime_sec:.4f} seconds

\\section{{Results}}

\\begin{{table}}[h]
\\centering
\\begin{{tabular}}{{ll}}
\\toprule
\\textbf{{Metric}} & \\textbf{{Value}} \\\\
\\midrule
CCC & {ccc:.4f} \\\\
RMSE & {rmse:.4f} \\\\
Runtime (s) & {b.runtime_sec:.4f} \\\\
Pass/Fail & {b.pass_fail} \\\\
\\bottomrule
\\end{{tabular}}
\\caption{{Statistical agreement metrics}}
\\end{{table}}

\\section{{Provenance}}
\\textbf{{Evidence Hash:}} \\texttt{{{b.evidence_hash}}}\\\\
\\textbf{{Bundle ID:}} \\texttt{{{b.bundle_id}}}\\\\
\\textbf{{Timestamp:}} {b.timestamp}

\\section{{Reproducibility}}
This evidence bundle can be reproduced by running:
\\begin{{verbatim}}
python examples/first_validation/demo.py --seed {b.random_seed}
\\end{{verbatim}}

\\end{{document}}
"""
```

### Tests
```python
def test_latex_generator_produces_valid_document():
    bundle = EvidenceBundle(evidence_hash="abc123", algorithm="CSP", dataset="PhysioNet", ...)
    tex = LaTeXReportGenerator(bundle).generate()
    assert "\\documentclass" in tex
    assert "\\begin{document}" in tex
    assert "\\end{document}" in tex
    assert "CSP" in tex
```

### Gemini Prompt
```
You are executing task S24. Create vireon-evidence/vireon_evidence/exporters/latex_generator.py — LaTeXReportGenerator class that takes an EvidenceBundle and produces a valid LaTeX document string. Must include: title, abstract with CCC, method section, results table, provenance section, reproducibility section. Write test verifying \documentclass, \begin{document}, \end{document}, algorithm name present. Branch: svp/S24-latex-paper-generator. TDD. Commit. PR. Stop.
```

---

## S25: Jupyter Notebook Generator

**Effort:** M | **Dependencies:** None | **Verification:** G6

### Implementation

Create `vireon-evidence/vireon_evidence/exporters/notebook_generator.py`:

```python
"""Generate an executable Jupyter notebook from an evidence bundle."""
import json
from vireon_core.contracts.evidence import EvidenceBundle

class NotebookGenerator:
    def __init__(self, bundle: EvidenceBundle):
        self.bundle = bundle
    
    def generate(self) -> dict:
        """Returns a Jupyter notebook dict (nbformat 4)."""
        b = self.bundle
        cells = [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    f"# VIREON Evidence Report\n\n",
                    f"**Algorithm:** {b.algorithm}\n\n",
                    f"**Dataset:** {b.dataset}\n\n",
                    f"**Evidence Hash:** `{b.evidence_hash[:32]}...`\n\n",
                    f"**Pass/Fail:** {b.pass_fail}\n"
                ]
            },
            {
                "cell_type": "code",
                "metadata": {},
                "execution_count": None,
                "outputs": [],
                "source": [
                    "import json\n",
                    "import numpy as np\n",
                    f"from vireon_methods.machine_learning.csp import CSPPlugin\n",
                    "from vireon_validation.benchmarks.matrix import BenchmarkMatrix\n\n",
                    "# Reproduce the evidence bundle\n",
                    f"seed = {b.random_seed}\n",
                    "matrix = BenchmarkMatrix(seed=seed)\n",
                    "csp = CSPPlugin(n_components=2)\n",
                    "matrix.add_method(csp)\n",
                    "# Add your dataset here\n",
                    "# matrix.add_dataset('...', data=X, labels=y)\n",
                    "bundles = matrix.execute_matrix()\n",
                    "print(f'CCC: {bundles[0][\"statistical_agreement\"][\"ccc\"]:.4f}')\n"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Results\n\n",
                    f"| Metric | Value |\n|--------|-------|\n",
                    f"| CCC | {b.statistical_agreement.get('ccc', 'N/A'):.4f} |\n",
                    f"| RMSE | {b.statistical_agreement.get('rmse', 'N/A'):.4f} |\n",
                    f"| Runtime | {b.runtime_sec:.4f}s |\n"
                ]
            }
        ]
        return {
            "nbformat": 4,
            "nbformat_minor": 5,
            "metadata": {
                "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                "language_info": {"name": "python", "version": "3.12.0"}
            },
            "cells": cells
        }
    
    def save(self, filepath: str):
        with open(filepath, "w") as f:
            json.dump(self.generate(), f, indent=2)
```

### Gemini Prompt
```
You are executing task S25. Create vireon-evidence/vireon_evidence/exporters/notebook_generator.py — NotebookGenerator class. generate() → nbformat 4 dict with markdown + code cells. save(filepath). Code cell must reproduce the evidence bundle (imports, seed, matrix setup). Write test verifying 'cells' in output, nbformat=4. Branch: svp/S25-jupyter-notebook-generator. TDD. Commit. PR. Stop.
```

---

## S26: FastAPI Backend

**Effort:** L | **Dependencies:** None | **Verification:** G7

### Implementation

Create `vireon-api/vireon_api/main.py`:

```python
"""FastAPI backend for VIREON evidence platform."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os, sys

# Add vireon packages to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'vireon-core'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'vireon-models'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'vireon-methods'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'vireon-validation'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'vireon-evidence'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'vireon-knowledge'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'vireon-corpus'))

app = FastAPI(title="VIREON Evidence API", version="0.4.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# In-memory evidence store (use SQLite in production)
_evidence_store = {}

class BenchmarkRequest(BaseModel):
    algorithm: str  # "csp", "welch", "ica"
    dataset: str    # "physionet_s1", "synthetic"
    seed: int = 42

@app.get("/api/health")
def health():
    return {"status": "ok", "version": "0.4.0"}

@app.get("/api/evidence")
def list_evidence():
    """List all evidence bundles."""
    return list(_evidence_store.values())

@app.get("/api/evidence/{evidence_hash}")
def get_evidence(evidence_hash: str):
    """Retrieve a specific evidence bundle."""
    if evidence_hash not in _evidence_store:
        raise HTTPException(status_code=404, detail="Evidence bundle not found")
    return _evidence_store[evidence_hash]

@app.post("/api/benchmark")
def run_benchmark(req: BenchmarkRequest):
    """Run a benchmark and return the evidence bundle."""
    import numpy as np
    from vireon_methods.machine_learning.csp import CSPPlugin
    from vireon_validation.benchmarks.matrix import BenchmarkMatrix
    
    # Generate synthetic data (or load real)
    rng = np.random.default_rng(req.seed)
    n_epochs, n_channels, n_samples = 30, 8, 250
    X = rng.normal(0, 1, (n_epochs, n_channels, n_samples))
    y = np.array([0, 1] * (n_epochs // 2))
    # Add class-discriminable signal
    for i in range(n_epochs):
        if y[i] == 0:
            X[i, :4] += 3 * np.sin(2*np.pi*10*np.arange(n_samples)/250)
        else:
            X[i, 4:] += 3 * np.sin(2*np.pi*10*np.arange(n_samples)/250)
    
    matrix = BenchmarkMatrix(seed=req.seed)
    matrix.add_method(CSPPlugin(n_components=2))
    matrix.add_dataset(req.dataset, data=X, labels=y)
    bundles = matrix.execute_matrix()
    
    if bundles:
        bundle = bundles[0]
        _evidence_store[bundle["evidence_hash"]] = bundle
        return {"evidence_hash": bundle["evidence_hash"], "ccc": bundle["statistical_agreement"]["ccc"], "pass_fail": bundle["pass_fail"]}
    raise HTTPException(status_code=500, detail="Benchmark failed")

@app.get("/api/algorithms")
def list_algorithms():
    """List available algorithms."""
    return [
        {"id": "csp", "name": "CSP+LDA", "srl": "SRL_2", "reference": "mne.decoding.CSP"},
        {"id": "welch", "name": "Welch PSD", "srl": "SRL_3", "reference": "scipy.signal.welch"},
        {"id": "ica", "name": "FastICA", "srl": "SRL_3", "reference": "sklearn.FastICA"},
        {"id": "fft", "name": "FFT", "srl": "SRL_3", "reference": "scipy.fft"},
    ]
```

### Gemini Prompt
```
You are executing task S26. Create vireon-api/vireon_api/main.py — FastAPI app with endpoints: GET /api/health, GET /api/evidence (list all), GET /api/evidence/{hash} (retrieve), POST /api/benchmark (run CSP+LDA on synthetic data, return hash+CCC+verdict), GET /api/algorithms (list available). Add fastapi+uvicorn to requirements. Write 3 tests using TestClient. Branch: svp/S26-fastapi-backend. TDD. Commit. PR. Stop.
```

---

## S27: HTML Dashboard

**Effort:** M | **Dependencies:** S26 | **Verification:** G7

### Implementation

Create `vireon-api/vireon_api/dashboard.html` — a static HTML page that fetches from the API:

```html
<!DOCTYPE html>
<html>
<head>
    <title>VIREON Evidence Dashboard</title>
    <style>
        body { font-family: sans-serif; margin: 2em; }
        .bundle { border: 1px solid #ccc; padding: 1em; margin: 1em 0; }
        .pass { color: green; font-weight: bold; }
        .fail { color: red; font-weight: bold; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    </style>
</head>
<body>
    <h1>VIREON Evidence Dashboard</h1>
    <button onclick="runBenchmark()">Run CSP Benchmark</button>
    <h2>Evidence Bundles</h2>
    <table id="bundles">
        <tr><th>Hash</th><th>Algorithm</th><th>Dataset</th><th>CCC</th><th>Status</th></tr>
    </table>
    <script>
        async function loadBundles() {
            const resp = await fetch('/api/evidence');
            const bundles = await resp.json();
            const table = document.getElementById('bundles');
            bundles.forEach(b => {
                const row = table.insertRow();
                row.insertCell().textContent = b.evidence_hash?.substring(0, 16) + '...';
                row.insertCell().textContent = b.algorithm || '';
                row.insertCell().textContent = b.dataset || '';
                row.insertCell().textContent = b.statistical_agreement?.ccc?.toFixed(4) || 'N/A';
                const status = row.insertCell();
                status.textContent = b.pass_fail || 'UNKNOWN';
                status.className = b.pass_fail === 'PASS' ? 'pass' : 'fail';
            });
        }
        async function runBenchmark() {
            const resp = await fetch('/api/benchmark', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({algorithm: 'csp', dataset: 'synthetic', seed: 42})
            });
            const result = await resp.json();
            alert(`Benchmark complete: CCC=${result.ccc?.toFixed(4)}, Status=${result.pass_fail}`);
            location.reload();
        }
        loadBundles();
    </script>
</body>
</html>
```

Add route in `main.py`:
```python
from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
def dashboard():
    with open(os.path.join(os.path.dirname(__file__), "dashboard.html")) as f:
        return f.read()
```

### Gemini Prompt
```
You are executing task S27. Create vireon-api/vireon_api/dashboard.html — static HTML dashboard. Fetches /api/evidence, displays table of bundles (hash, algorithm, dataset, CCC, status). "Run Benchmark" button calls POST /api/benchmark. Add GET / route in main.py to serve dashboard. Branch: svp/S27-html-dashboard. Commit. PR. Stop. Depends on S26.
```

---

## S28: Tutorial Suite

**Effort:** M | **Dependencies:** All | **Verification:** G1

### Implementation

Create 4 tutorials in `docs/tutorials/`:

1. **`01_quickstart.md`** — Install VIREON, run the demo, inspect evidence.json
2. **`02_algorithm_validation.md`** — How to validate a custom algorithm against scipy/MNE
3. **`03_literature_reproduction.md`** — How to reproduce a published paper
4. **`04_evidence_graph.md`** — How to use the evidence graph, queries, and leaderboard

Each tutorial must be verified against current code (no drift).

### Gemini Prompt
```
You are executing task S28. Create 4 tutorials in docs/tutorials/: 01_quickstart.md (install, run demo, inspect evidence.json), 02_algorithm_validation.md (validate custom algorithm vs scipy/MNE), 03_literature_reproduction.md (reproduce a paper with real data), 04_evidence_graph.md (graph queries, leaderboard, meta-analysis). Each tutorial must have working code examples verified against current code. Branch: svp/S28-tutorial-suite. Commit. PR. Stop.
```

---

## S29: API Reference Generator

**Effort:** S | **Dependencies:** None | **Verification:** G1

### Implementation

Create `scripts/generate_api_reference.py`:

```python
"""Auto-generate API reference from docstrings using mkdocstrings."""
import os, subprocess

PACKAGES = ["vireon_core", "vireon_methods", "vireon_validation", "vireon_evidence", "vireon_models", "vireon_knowledge", "vireon_corpus"]

def generate():
    os.makedirs("docs/api", exist_ok=True)
    with open("docs/api_reference.md", "w") as f:
        f.write("# VIREON API Reference\n\n")
        for pkg in PACKAGES:
            f.write(f"## {pkg}\n\n")
            f.write(f"::: {pkg}\n\n")
    print("API reference: docs/api_reference.md")
    # Optionally build with mkdocs
    # subprocess.run(["mkdocs", "build"])

if __name__ == "__main__":
    generate()
```

### Gemini Prompt
```
You are executing task S29. Create scripts/generate_api_reference.py that generates docs/api_reference.md with mkdocstrings ::: package directives for all 7 vireon packages. Run: python scripts/generate_api_reference.py. Verify file > 50 lines. Branch: svp/S29-api-reference-generator. Commit. PR. Stop.
```

---

## S30: Final Integration — Verify V1-V15, Tag v0.4.0

**Effort:** M | **Dependencies:** ALL | **Verification:** ALL

### Implementation

Run all 15 success criteria (V1-V15). If all pass, tag `v0.4.0-scientific-validation-platform` and write release notes.

```bash
# V1: Algorithm validation suite
pytest tests/test_algorithm_validation_suite/ -v

# V2: Validation report
ls reports/algorithm_validation_report.md

# V3: Literature reproduction
pytest vireon-verification/literature/ -v

# V4-V6: Statistical rigor
rg "bootstrap_ci|compute_bootstrap" vireon-validation/
rg "permutation_test" vireon-validation/
rg "fdr_correction|benjamini" vireon-validation/

# V7: Evidence persistence
python -c "from vireon_evidence.graph.core import EvidenceGraph; ..."

# V8-V9: Publication outputs
python -c "from vireon_evidence.exporters.latex_generator import LaTeXReportGenerator; ..."
python -c "from vireon_evidence.exporters.notebook_generator import NotebookGenerator; ..."

# V10-V11: REST API
curl localhost:8000/api/evidence
curl -X POST localhost:8000/api/benchmark -d '{"algorithm":"csp","dataset":"synthetic"}'

# V12: Tutorials
ls docs/tutorials/*.md

# V13: API reference
python scripts/generate_api_reference.py && ls docs/api_reference.md

# V14: Full test suite
pytest --tb=no -q

# V15: Coverage
pytest --cov=vireon-validation --cov=vireon-evidence --cov-fail-under=75

# Tag
git tag -a v0.4.0-scientific-validation-platform -m "Scientific Validation Platform"
```

### Gemini Prompt
```
You are executing task S30, the FINAL task. Run all 15 success criteria (V1-V15 from the playbook). If all pass: tag v0.4.0-scientific-validation-platform, write RELEASE_NOTES_v0.4.0.md. If any fail: write BLOCKED.md, do NOT tag. Branch: svp/S30-final-integration. Commit. PR. Stop. Depends on ALL.
```
