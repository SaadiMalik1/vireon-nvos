"""Generate a regulatory audit binder from evidence bundles.

Produces a directory structure with:
  binder/
    cover_sheet.json         # 510(k) cover sheet fields
    vmp.md                   # Validation Master Plan (rendered from template)
    soup_inventory.md        # SOUP inventory (auto-generated from pyproject.toml)
    gmlp_compliance.md       # GMLP principle mapping
    evidence_summary.json    # Aggregate of all evidence bundles
    evidence_bundles/        # Individual bundle JSON files
      <hash>.json
    test_results/            # Pytest results
      junit.xml
      summary.json
    signature_block.txt      # Cryptographic signature placeholder
    manifest.json            # Index of all binder files
"""
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field

from vireon_evidence.registry.core import EvidenceRegistry


class BinderConfig(BaseModel):
    device_name: str = Field(default="VIREON-Validated BCI Decoder", description="Device name")
    device_version: str = Field(default="1.1.0", description="Device version")
    submission_type: str = Field(default="510(k)", description="510(k), PMA, De Novo, etc.")
    predicate_device: Optional[str] = Field(default=None, description="Substantial equivalence predicate")
    manufacturer_name: str = Field(default="VIREON Project", description="Manufacturer name")
    manufacturer_address: str = Field(default="N/A", description="Manufacturer address")
    contact_email: str = Field(default="maintainers@vireon.org", description="Contact email")
    regulatory_class: str = Field(default="II", description="Regulatory class I, II, or III")


class RegulatoryBinderGenerator:
    """Generate a regulatory audit binder from evidence + tests + metadata."""

    def __init__(self, registry: EvidenceRegistry, config: BinderConfig):
        self.registry = registry
        self.config = config
        self.binder_dir: Optional[Path] = None

    def generate(self, output_dir: str, run_tests: bool = True) -> Path:
        """Generate the complete binder directory.

        Args:
            output_dir: Directory to create the binder in.
            run_tests: If True, run pytest and export JUnit results.

        Returns:
            Path to generated binder directory.
        """
        self.binder_dir = Path(output_dir) / f"binder_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.binder_dir.mkdir(parents=True, exist_ok=True)

        self._write_cover_sheet()
        self._write_vmp()
        self._write_soup_inventory()
        self._write_gmlp_mapping()
        self._write_evidence_summary()
        self._export_evidence_bundles()
        if run_tests:
            self._run_and_export_tests()
        self._write_signature_block()
        self._write_manifest()

        return self.binder_dir

    def _write_cover_sheet(self):
        cover = {
            "submission_type": self.config.submission_type,
            "device_name": self.config.device_name,
            "device_version": self.config.device_version,
            "manufacturer": {
                "name": self.config.manufacturer_name,
                "address": self.config.manufacturer_address,
                "contact_email": self.config.contact_email,
            },
            "regulatory_class": self.config.regulatory_class,
            "predicate_device": self.config.predicate_device,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generator": "VIREON RegulatoryBinderGenerator v1.1.0",
        }
        with open(self.binder_dir / "cover_sheet.json", "w") as f:
            json.dump(cover, f, indent=2)

    def _write_vmp(self):
        template_path = Path("docs/regulatory/validation_master_plan.md")
        if template_path.exists():
            template = template_path.read_text()
        else:
            template = "# Validation Master Plan\n\n(Template missing)"

        vmp = template.replace("{{DEVICE_NAME}}", self.config.device_name)
        vmp = vmp.replace("{{DEVICE_VERSION}}", self.config.device_version)
        vmp = vmp.replace("{{DATE}}", datetime.now().strftime("%Y-%m-%d"))

        with open(self.binder_dir / "vmp.md", "w") as f:
            f.write(vmp)

    def _write_soup_inventory(self):
        pp_path = Path("pyproject.toml")
        if not pp_path.exists():
            return

        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                tomllib = None

        if tomllib:
            with open(pp_path, "rb") as f:
                pp = tomllib.load(f)
            deps = pp.get("project", {}).get("dependencies", [])
        else:
            deps = ["numpy>=1.24.0", "scipy>=1.10.0", "torch>=2.0.0", "mne>=1.3.0", "pydantic>=2.0.0"]

        soup_rows = []
        soup_rows.append("| Package | Version Spec | IEC 62304 Class | Risk Level | Source |")
        soup_rows.append("|---------|--------------|-----------------|------------|--------|")
        for dep in deps:
            name, version_spec = dep.strip(), "(unpinned)"
            for sep in [">=", "<=", "==", ">", "<", "~="]:
                if sep in dep:
                    parts = dep.split(sep, 1)
                    name = parts[0].strip()
                    version_spec = f"{sep}{parts[1].strip()}"
                    break

            if name in ["numpy", "scipy", "scikit-learn"]:
                iec_class, risk = "A", "Low"
            elif name in ["torch", "mne", "pydantic"]:
                iec_class, risk = "B", "Medium"
            else:
                iec_class, risk = "A", "Low"

            soup_rows.append(f"| {name} | {version_spec} | {iec_class} | {risk} | PyPI |")

        with open(self.binder_dir / "soup_inventory.md", "w") as f:
            f.write("# SOUP (Software of Unknown Provenance) Inventory\n\n")
            f.write(f"Auto-generated from pyproject.toml on {datetime.now(timezone.utc).isoformat()}\n\n")
            f.write("\n".join(soup_rows))
            f.write("\n")

    def _write_gmlp_mapping(self):
        gmlp_principles = [
            ("1. Define and document the algorithm's intended use",
             "See cover_sheet.json 'device_name' and VMP §2"),
            ("2. Define the algorithm's inputs and outputs",
             "See EvidenceBundle schema in vireon-core/contracts/evidence.py"),
            ("3. Define the algorithm's performance characteristics",
             "See evidence_summary.json for CCC, RMSE, accuracy metrics"),
            ("4. Define the algorithm's failure modes and warnings",
             "See ScientificContractViolation in vireon-core/contracts/plugin.py"),
            ("5. Define how the algorithm will be evaluated",
             "See vireon-validation/benchmarks/matrix.py BenchmarkMatrix"),
            ("6. Define the reference standard",
             "See vireon-methods/validation/comparison_engine.py (scipy/sklearn/MNE references)"),
            ("7. Define the test data",
             "See evidence_bundles/*.json 'dataset' field"),
            ("8. Define the statistical analysis plan",
             "See vireon-validation/statistics/framework.py (CCC, bootstrap CI)"),
            ("9. Define how the algorithm will be monitored",
             "See vireon-validation/regression/detector.py ScientificRegressionDetector"),
            ("10. Define how the algorithm will be maintained",
             "See REMEDIATION_STATUS.md and CHANGELOG.md"),
        ]
        with open(self.binder_dir / "gmlp_compliance.md", "w") as f:
            f.write("# FDA GMLP Compliance Mapping\n\n")
            f.write("Reference: FDA Good Machine Learning Practice for Medical Device Development\n\n")
            for principle, mapping in gmlp_principles:
                f.write(f"## {principle}\n\n{mapping}\n\n")

    def _write_evidence_summary(self):
        bundle_dicts = self.registry.list_bundles()
        summary = {
            "total_bundles": len(bundle_dicts),
            "algorithms_tested": list(set(b["algorithm"] for b in bundle_dicts)),
            "datasets_used": list(set(b["dataset"] for b in bundle_dicts)),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        with open(self.binder_dir / "evidence_summary.json", "w") as f:
            json.dump(summary, f, indent=2)

    def _export_evidence_bundles(self):
        bundles_dir = self.binder_dir / "evidence_bundles"
        bundles_dir.mkdir(exist_ok=True)
        for entry in self.registry.list_bundles():
            evidence_hash = entry["hash"]
            bundle = self.registry.retrieve(evidence_hash)
            if bundle:
                path = bundles_dir / f"{evidence_hash}.json"
                path.write_text(bundle.model_dump_json(indent=2))

    def _run_and_export_tests(self):
        test_dir = self.binder_dir / "test_results"
        test_dir.mkdir(exist_ok=True)

        junit_path = test_dir / "junit.xml"
        try:
            subprocess.run(
                ["python3", "-m", "pytest",
                 "--junitxml", str(junit_path),
                 "--tb=short", "-q"],
                check=False,
                capture_output=True,
                text=True,
                timeout=3600,
            )
        except subprocess.TimeoutExpired:
            with open(test_dir / "timeout.txt", "w") as f:
                f.write("pytest timed out after 1 hour")

        summary = {"junit_xml": str(junit_path), "generated_at": datetime.now(timezone.utc).isoformat()}
        with open(test_dir / "summary.json", "w") as f:
            json.dump(summary, f, indent=2)

    def _write_signature_block(self):
        with open(self.binder_dir / "signature_block.txt", "w") as f:
            f.write("Regulatory Audit Binder Signature Block\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Device: {self.config.device_name} v{self.config.device_version}\n")
            f.write(f"Generated: {datetime.now(timezone.utc).isoformat()}\n\n")
            f.write("Signer Name: ______________________________\n")
            f.write("Signer Title: ______________________________\n")
            f.write("Signature: ______________________________\n")
            f.write("Date: ______________________________\n\n")
            f.write("NOTE: This is a placeholder. For FDA submission, use eCopy format\n")
            f.write("with digital signature per 21 CFR Part 11.\n")

    def _write_manifest(self):
        files = []
        for path in sorted(self.binder_dir.rglob("*")):
            if path.is_file():
                rel = path.relative_to(self.binder_dir)
                files.append({
                    "path": str(rel),
                    "size_bytes": path.stat().st_size,
                    "modified": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat(),
                })
        with open(self.binder_dir / "manifest.json", "w") as f:
            json.dump({"files": files, "total": len(files)}, f, indent=2)
