"""Regulatory Submission Example: Generate a 510(k) audit binder.

This script generates a real (if minimal) audit binder directory containing:
  - Cover sheet with device and manufacturer info
  - Validation Master Plan (rendered from docs/regulatory/validation_master_plan.md)
  - SOUP inventory (auto-generated from pyproject.toml dependencies)
  - FDA GMLP compliance mapping (all 10 principles)
  - Evidence summary (aggregated from EvidenceRegistry)
  - Individual evidence bundle JSON exports
  - Pytest JUnit XML results
  - Signature block (placeholder for 21 CFR Part 11)
  - Manifest (index of all files)

Usage:
  python examples/example_regulatory_submission.py --output ./audit_binder

The generated binder is suitable as a starting point for a 510(k) submission
but is NOT a substitute for regulatory review by qualified professionals.
"""
import argparse

from vireon_evidence.regulatory.binder_generator import (
    RegulatoryBinderGenerator, BinderConfig,
)
from vireon_evidence.registry.core import EvidenceRegistry


def main():
    parser = argparse.ArgumentParser(description="Generate VIREON regulatory audit binder")
    parser.add_argument("--output", default="./audit_binder", help="Output directory")
    parser.add_argument("--device-name", default="VIREON-Validated BCI Decoder")
    parser.add_argument("--device-version", default="1.1.0")
    parser.add_argument("--manufacturer", default="VIREON Project")
    parser.add_argument("--address", default="N/A")
    parser.add_argument("--email", default="maintainers@vireon.org")
    parser.add_argument("--predicate", default=None, help="Predicate device for substantial equivalence")
    parser.add_argument("--no-tests", action="store_true", help="Skip pytest execution")
    args = parser.parse_args()

    config = BinderConfig(
        device_name=args.device_name,
        device_version=args.device_version,
        manufacturer_name=args.manufacturer,
        manufacturer_address=args.address,
        contact_email=args.email,
        predicate_device=args.predicate,
    )

    registry = EvidenceRegistry()
    generator = RegulatoryBinderGenerator(registry, config)

    binder_path = generator.generate(
        output_dir=args.output,
        run_tests=not args.no_tests,
    )
    print(f"[Regulatory Submission] Generated audit binder at: {binder_path}")
    print(f"  Files generated: {len(list(binder_path.rglob('*')))}")
    print(f"  Manifest: {binder_path / 'manifest.json'}")
    print()
    print("NOTE: This binder is a starting point. For FDA submission:")
    print("  1. Review all generated files with regulatory counsel")
    print("  2. Convert to FDA eCopy format")
    print("  3. Apply digital signature per 21 CFR Part 11")
    print("  4. Submit via FDA Electronic Submission Gateway")


if __name__ == "__main__":
    main()
