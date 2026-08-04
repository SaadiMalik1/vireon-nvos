from typing import Dict, Any
from vireon_core.contracts.evidence import EvidenceBundle


class EvidenceIdentifier:
    """
    Evidence Identifier for VIREON evidence bundles (DataCite DOI format).
    """
    def __init__(self, prefix: str = "10.5072/vireon"):
        self.prefix = prefix

    def mint(self, bundle: EvidenceBundle) -> str:
        """Mint a DOI for an evidence bundle."""
        suffix = bundle.evidence_hash[:16] if bundle.evidence_hash else bundle.bundle_id[:16]
        return f"{self.prefix}/{suffix}"

    def mint_with_metadata(self, bundle: EvidenceBundle) -> Dict[str, Any]:
        """Mint a DOI along with DataCite metadata."""
        doi = self.mint(bundle)
        ccc = "N/A"
        if hasattr(bundle, "statistical_agreement") and isinstance(bundle.statistical_agreement, dict):
            ccc = bundle.statistical_agreement.get("ccc", "N/A")
        elif hasattr(bundle, "metrics") and isinstance(bundle.metrics, dict):
            ccc = bundle.metrics.get("ccc", "N/A")

        return {
            "doi": doi,
            "title": f"VIREON Evidence Bundle: {bundle.algorithm} on {bundle.dataset}",
            "creator": "VIREON NVOS",
            "publisher": "VIREON",
            "publication_year": 2025,
            "resource_type": "Dataset",
            "description": f"Evidence bundle with CCC={ccc}",
            "url": f"https://vireon.org/evidence/{bundle.evidence_hash}"
        }
