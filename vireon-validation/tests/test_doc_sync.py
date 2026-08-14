import unittest
from scripts.check_doc_sync import run_checks

class TestDocSyncChecker(unittest.TestCase):
    def test_all_claims_verified_no_drift(self):
        """All real doc claims should pass without drift."""
        failures = run_checks()
        self.assertEqual(len(failures), 0, f"Expected 0 drifts, got: {failures}")

    def test_detects_drift_when_claim_false(self):
        """Should detect and report drift when a claim rule returns False."""
        fake_claims = [
            {
                "doc": "docs/fake.md",
                "claim": "Fake feature exists",
                "verify": lambda: False,
            }
        ]
        failures = run_checks(fake_claims)
        self.assertEqual(len(failures), 1)
        self.assertIn("DRIFT: docs/fake.md — Fake feature exists", failures[0])

if __name__ == "__main__":
    unittest.main()
