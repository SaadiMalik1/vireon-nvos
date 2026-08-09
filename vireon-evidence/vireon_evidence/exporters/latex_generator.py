"""Generate a LaTeX paper from an evidence bundle."""
from datetime import datetime
from vireon_core.contracts.evidence import EvidenceBundle


class LaTeXReportGenerator:
    """
    Generate a LaTeX paper report from an EvidenceBundle.
    """
    def __init__(self, bundle: EvidenceBundle):
        self.bundle = bundle

    def generate(self) -> str:
        b = self.bundle
        stat_aggr = getattr(b, "statistical_agreement", {}) or getattr(b, "metrics", {})
        if not isinstance(stat_aggr, dict):
            stat_aggr = {}
        ccc_val = stat_aggr.get("ccc", 0.0)
        rmse_val = stat_aggr.get("rmse", 0.0)

        ccc_str = f"{float(ccc_val):.4f}" if isinstance(ccc_val, (int, float)) else str(ccc_val)
        rmse_str = f"{float(rmse_val):.4f}" if isinstance(rmse_val, (int, float)) else str(rmse_val)

        pass_fail = getattr(b, "pass_fail", "PASS")
        hash_prefix = b.evidence_hash[:32] if b.evidence_hash else b.bundle_id[:32]
        date_str = datetime.now().strftime("%B %d, %Y")

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
\\date{{{date_str}}}

\\begin{{document}}
\\maketitle

\\begin{{abstract}}
This report documents the validation of {b.algorithm} on the {b.dataset} dataset.
The evidence bundle hash is \\texttt{{{hash_prefix}...}}.
The concordance correlation coefficient (CCC) between the method under test and
the reference implementation is {ccc_str}.
The pass/fail verdict is: \\textbf{{{pass_fail}}}.
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
CCC & {ccc_str} \\\\
RMSE & {rmse_str} \\\\
Runtime (s) & {b.runtime_sec:.4f} \\\\
Pass/Fail & {pass_fail} \\\\
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
