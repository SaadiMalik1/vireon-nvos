"""Evidence export formats (JSON-LD, BibTeX, RDF/Turtle)."""
from typing import Dict, Any
from vireon_core.contracts.evidence import EvidenceBundle


def export_to_jsonld(bundle: EvidenceBundle) -> Dict[str, Any]:
    """Export evidence bundle as Schema.org JSON-LD."""
    h = bundle.evidence_hash if bundle.evidence_hash else bundle.bundle_id
    stat_aggr = getattr(bundle, "statistical_agreement", {}) or getattr(bundle, "metrics", {})
    return {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "@id": f"https://vireon.org/evidence/{h}",
        "name": f"VIREON Evidence: {bundle.algorithm}",
        "creator": "VIREON NVOS",
        "datePublished": str(bundle.timestamp),
        "measurementTechnique": bundle.algorithm,
        "variableMeasured": stat_aggr,
    }


def export_to_bibtex(bundle: EvidenceBundle) -> str:
    """Export evidence bundle as BibTeX entry."""
    h = bundle.evidence_hash if bundle.evidence_hash else bundle.bundle_id
    key = h[:16]
    return f"""@dataset{{{key},
  title = {{VIREON Evidence: {bundle.algorithm}}},
  author = {{VIREON NVOS}},
  year = {{2025}},
  doi = {{10.5072/vireon/{key}}},
  url = {{https://vireon.org/evidence/{h}}}
}}"""


def export_to_turtle(bundle: EvidenceBundle) -> str:
    """Export evidence bundle as RDF Turtle."""
    h = bundle.evidence_hash if bundle.evidence_hash else bundle.bundle_id
    return f"""@prefix schema: <https://schema.org/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<https://vireon.org/evidence/{h}> a schema:Dataset ;
    schema:name "VIREON Evidence: {bundle.algorithm}" ;
    schema:creator "VIREON NVOS" ;
    schema:datePublished "{bundle.timestamp}"^^xsd:dateTime ;
    schema:measurementTechnique "{bundle.algorithm}" .
"""
