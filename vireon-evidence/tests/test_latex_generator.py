from vireon_core.contracts.evidence import EvidenceBundle
from vireon_evidence.exporters.latex_generator import LaTeXReportGenerator


def test_latex_generator_produces_valid_document():
    bundle = EvidenceBundle(
        evidence_hash="abc1234567890def1234567890",
        algorithm="CSP",
        dataset="PhysioNet",
        runtime_sec=0.1234
    )
    tex = LaTeXReportGenerator(bundle).generate()
    assert "\\documentclass" in tex
    assert "\\begin{document}" in tex
    assert "\\end{document}" in tex
    assert "CSP" in tex
    assert "PhysioNet" in tex
    assert "\\begin{table}" in tex
