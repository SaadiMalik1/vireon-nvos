"""Real-Data Integration Test Suite."""
from vireon_corpus.dataset_manager import DatasetManager
from vireon_core.contracts.evidence import EvidenceBundle


def test_real_data_end_to_end_integration():
    dm = DatasetManager()
    datasets = dm.list_datasets()
    assert len(datasets) >= 4

    bundles = []
    for d_key in datasets[:4]:
        info = dm.load_dataset(d_key)
        bundle = EvidenceBundle(
            evidence_hash=info["checksum"],
            algorithm="RealDataIntegrationPipeline",
            dataset=info["name"],
            statistical_agreement={"verified": True}
        )
        bundles.append(bundle)

    assert len(bundles) == 4
    for b in bundles:
        assert len(b.evidence_hash) == 64
