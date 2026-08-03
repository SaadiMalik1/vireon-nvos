import os
from vireon_core.contracts.evidence import EvidenceBundle
from vireon_evidence.exporters.notebook_generator import NotebookGenerator


def test_notebook_generator_structure(tmp_path):
    bundle = EvidenceBundle(
        evidence_hash="abcdef1234567890abcdef1234567890",
        algorithm="CSP",
        dataset="Synthetic",
        runtime_sec=0.45
    )
    gen = NotebookGenerator(bundle)
    nb = gen.generate()

    assert nb["nbformat"] == 4
    assert len(nb["cells"]) == 3
    assert any(c["cell_type"] == "code" for c in nb["cells"])
    assert any(c["cell_type"] == "markdown" for c in nb["cells"])

    out_file = str(tmp_path / "test_nb.ipynb")
    gen.save(out_file)
    assert os.path.exists(out_file)
