import json
from vireon_evidence.registry.core import EvidenceRegistry
from vireon_evidence.regulatory.binder_generator import RegulatoryBinderGenerator, BinderConfig
from vireon_core.contracts.evidence import EvidenceBundle


def test_regulatory_binder_generator(tmp_path):
    db_path = str(tmp_path / "registry.db")
    reg = EvidenceRegistry(db_path=db_path)

    bundle = EvidenceBundle(
        evidence_hash="test_hash_abc123",
        algorithm="VireonWelch",
        dataset="PhysioNet",
        statistical_agreement={"ccc": 0.99},
    )
    reg.register(bundle)

    config = BinderConfig(
        device_name="Test EEG Decoder",
        device_version="1.0.0",
        manufacturer_name="VIREON Labs",
    )

    generator = RegulatoryBinderGenerator(reg, config)
    out_dir = str(tmp_path / "out")
    binder_dir = generator.generate(output_dir=out_dir, run_tests=False)

    assert binder_dir.exists()
    assert (binder_dir / "cover_sheet.json").exists()
    assert (binder_dir / "vmp.md").exists()
    assert (binder_dir / "soup_inventory.md").exists()
    assert (binder_dir / "gmlp_compliance.md").exists()
    assert (binder_dir / "evidence_summary.json").exists()
    assert (binder_dir / "signature_block.txt").exists()
    assert (binder_dir / "manifest.json").exists()

    with open(binder_dir / "soup_inventory.md") as f:
        content = f.read()
        assert "Auto-generated from pyproject.toml" in content

    with open(binder_dir / "manifest.json") as f:
        manifest = json.load(f)
        assert manifest["total"] > 0
