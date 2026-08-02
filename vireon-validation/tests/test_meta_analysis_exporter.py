import os
import json
import pytest
import numpy as np
from vireon_validation.benchmarks.meta_analysis import MetaAnalysisEngine, PublicationExporter

def test_meta_analysis_engine():
    results = [
        {"dataset": "ds1", "score": 0.90, "variance": 0.002},
        {"dataset": "ds2", "score": 0.85, "variance": 0.003},
        {"dataset": "ds3", "score": 0.95, "variance": 0.001},
    ]
    engine = MetaAnalysisEngine(results)
    stats = engine.compute_statistics()
    assert abs(stats["global_mean_performance"] - 0.90) < 1e-4
    assert stats["confidence_interval"][0] < stats["global_mean_performance"] < stats["confidence_interval"][1]
    assert stats["between_dataset_variance"] >= 0.0

def test_publication_exporter_writes_files(tmp_path):
    results = {
        "global_mean_performance": 0.92,
        "confidence_interval": [0.88, 0.96],
        "heterogeneity_i2": 15.0,
        "studies": [
            {"study": "Study A", "effect_size": 0.91, "variance": 0.002},
            {"study": "Study B", "effect_size": 0.93, "variance": 0.001}
        ]
    }
    exporter = PublicationExporter(results)
    written_files = exporter.export(str(tmp_path))
    
    assert len(written_files) >= 3
    for f in written_files:
        assert os.path.exists(f)
        assert os.path.getsize(f) > 0
        
    # Check JSON content
    json_files = [f for f in written_files if f.endswith(".json")]
    assert len(json_files) >= 1
    with open(json_files[0], "r") as jf:
        data = json.load(jf)
        assert data["global_mean_performance"] == 0.92
