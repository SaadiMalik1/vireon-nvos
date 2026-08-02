import os
from pathlib import Path
from vireon_lab.experiments.schema import load_experiment_from_yaml
from vireon_core.kernel.execution_engine import ExecutionEngine
from vireon_validation.evidence.generator import EvidenceGenerator

SCENARIOS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "vireon_validation", "benchmarks", "scenarios")
)

def test_no_fake_parquet_written(tmp_path):
    filepath = os.path.join(SCENARIOS_DIR, "01_baseline_eeg.yaml")
    scenario = load_experiment_from_yaml(filepath)
    engine = ExecutionEngine(scenario, seed=42)
    evidence = engine.execute()
    
    gen = EvidenceGenerator(evidence, str(tmp_path))
    
    # Generate bundle without raw data
    bundle_path = gen.generate_bundle(raw_provider_data=None)
    
    parquet_files = list(Path(bundle_path).rglob("*.parquet"))
    forbidden_stub = b"PARQUET_" + b"STUB_DATA"
    for f in parquet_files:
        content = f.read_bytes()
        assert content != forbidden_stub, f"{f} contains fake stub"
        try:
            import pyarrow.parquet as pq
            pq.read_table(str(f))
        except ImportError:
            pass

    # Ensure no parquet file was written if no raw data
    assert len(parquet_files) == 0, "Fake parquet file was generated when raw_provider_data is None"
