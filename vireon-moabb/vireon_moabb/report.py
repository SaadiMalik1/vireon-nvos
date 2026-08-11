class Scorecard:
    """Final compliance scorecard for a pipeline/dataset combination."""

    def __init__(self, bundle):
        self.bundle = bundle
        self.grade = self._compute_grade()

    def _compute_grade(self) -> str:
        acc = self.bundle.summary.get("mean_accuracy", 0.0)
        passed = self.bundle.summary.get("all_validation_passed", False)
        if not passed:
            return "FAIL"
        if acc >= 0.8: return "A"
        if acc >= 0.7: return "B"
        if acc >= 0.6: return "C"
        return "D"

    def to_markdown(self) -> str:
        return f"""# Algorithm Compliance Scorecard
**Grade**: {self.grade}
**Accuracy**: {self.bundle.summary.get("mean_accuracy", 0):.4f}
**Dataset**: {self.bundle.summary.get("dataset", "Unknown")}
**Evidence Hash**: `{self.bundle.evidence_hash}`
"""

class Reporter:
    def generate_raw_evidence_report(self, trace, validation, bundle) -> str:
        return f"Raw Evidence Report for {bundle.bundle_id}\nACC:{trace.mean_accuracy:.4f}\nHASH:{bundle.evidence_hash}"

    def generate_scorecard(self, bundle) -> str:
        sc = Scorecard(bundle)
        return sc.to_markdown()
