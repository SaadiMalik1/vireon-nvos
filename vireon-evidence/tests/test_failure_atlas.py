import os
import tempfile
import unittest
from vireon_evidence.registry.failure_atlas import FailureAtlas

class TestFailureAtlas(unittest.TestCase):
    def test_persistence_survives_restart(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_atlas.db")
            atlas1 = FailureAtlas(db_path=db_path)
            
            record = {
                "method_id": "method_a",
                "dataset_id": "ds_1",
                "timestamp": "2026-08-02T00:00:00Z",
                "error_metrics": {"loss": 99.9}
            }
            h = atlas1.register_failure(record)
            
            # Restart instance
            atlas2 = FailureAtlas(db_path=db_path)
            retrieved = atlas2.get_failure(h)
            self.assertIsNotNone(retrieved)
            self.assertEqual(retrieved["method_id"], "method_a")
            self.assertEqual(retrieved["reproducibility_hash"], h)
            
            atlas1.close()
            atlas2.close()

    def test_list_failures_filter(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_atlas.db")
            atlas = FailureAtlas(db_path=db_path)
            
            atlas.register_failure({"method_id": "method_a", "dataset_id": "ds_1"})
            atlas.register_failure({"method_id": "method_b", "dataset_id": "ds_2"})
            atlas.register_failure({"method_id": "method_a", "dataset_id": "ds_3"})
            
            all_f = atlas.list_failures()
            self.assertEqual(len(all_f), 3)
            
            method_a_f = atlas.list_failures(method_id="method_a")
            self.assertEqual(len(method_a_f), 2)
            for f in method_a_f:
                self.assertEqual(f["method_id"], "method_a")
                
            atlas.close()
