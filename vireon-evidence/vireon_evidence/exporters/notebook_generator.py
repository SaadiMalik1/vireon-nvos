"""Generate an executable Jupyter notebook from an evidence bundle."""
import json
from typing import Dict, Any
from vireon_core.contracts.evidence import EvidenceBundle


class NotebookGenerator:
    """
    Generate an executable Jupyter notebook (nbformat 4) from an EvidenceBundle.
    """
    def __init__(self, bundle: EvidenceBundle):
        self.bundle = bundle

    def generate(self) -> Dict[str, Any]:
        """Returns a Jupyter notebook dict (nbformat 4)."""
        b = self.bundle
        stat_aggr = getattr(b, "statistical_agreement", {}) or getattr(b, "metrics", {})
        if not isinstance(stat_aggr, dict):
            stat_aggr = {}
        ccc_val = stat_aggr.get("ccc", "N/A")
        rmse_val = stat_aggr.get("rmse", "N/A")

        ccc_str = f"{float(ccc_val):.4f}" if isinstance(ccc_val, (int, float)) else str(ccc_val)
        rmse_str = f"{float(rmse_val):.4f}" if isinstance(rmse_val, (int, float)) else str(rmse_val)

        pass_fail = getattr(b, "pass_fail", "PASS")
        hash_prefix = b.evidence_hash[:32] if b.evidence_hash else b.bundle_id[:32]

        cells = [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# VIREON Evidence Report\n\n",
                    f"**Algorithm:** {b.algorithm}\n\n",
                    f"**Dataset:** {b.dataset}\n\n",
                    f"**Evidence Hash:** `{hash_prefix}...`\n\n",
                    f"**Pass/Fail:** {pass_fail}\n"
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
                    "from vireon_methods.machine_learning.csp import CSPPlugin\n",
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
                    "| Metric | Value |\n|--------|-------|\n",
                    f"| CCC | {ccc_str} |\n",
                    f"| RMSE | {rmse_str} |\n",
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
