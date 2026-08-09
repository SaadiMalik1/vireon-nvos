from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vireon_simple.api import ExperimentResult

def generate_report(result: "ExperimentResult", format: str = "text") -> str:
    from vireon_simple.terminology import humanize
    
    acc = result.statistics.get("accuracy", 0) * 100
    report = []
    
    if result.scorecard and result.scorecard.total >= 80:
        report.append("✓ VALIDATED\n")
    else:
        report.append("⚠ VALIDATION ISSUES\n")
        
    report.append(f"Your algorithm achieved {acc:.1f}% accuracy.\n")
    report.append("Why?\n")
    
    if result.scorecard:
        for dim in result.scorecard.dimensions:
            icon = "✓" if dim.score == dim.max else ("⚠" if dim.score > 0 else "✗")
            report.append(f"{icon} {humanize(dim.name)}: {dim.explanation}")
            
    report.append(f"\nOverall confidence: {result.scorecard.confidence if result.scorecard else 'UNKNOWN'}")
    
    if getattr(result.provenance, "evidence_hash", None):
        report.append(f"Evidence hash: {result.provenance.evidence_hash}")
        
    return "\n".join(report)
