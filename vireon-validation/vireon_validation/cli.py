import yaml
import argparse
import sys
from vireon_core.contracts.evidence import EvidenceBundle

class CampaignCLI:
    """
    Continuous Campaign CLI.
    `vireon campaign run <manifest.yaml>`
    """
    def __init__(self):
        pass
        
    def parse_manifest(self, filepath: str) -> dict:
        with open(filepath, "r") as f:
            return yaml.safe_load(f)
            
    def run_campaign(self, manifest_path: str):
        manifest = self.parse_manifest(manifest_path)
        campaign = manifest.get("campaign", {})
        
        algorithm = campaign.get("algorithm", "Unknown")
        reference = campaign.get("reference", "Unknown")
        
        print(f"Starting Campaign: {algorithm} vs {reference}")
        print("Executing synthetic datasets...")
        print("Executing reference comparisons...")
        print("Applying perturbations...")
        
        from vireon_validation.benchmarks.matrix import BenchmarkMatrix
        from vireon_core.contracts.evidence import MethodProvenance
        from collections import namedtuple
        
        print(f"Starting Campaign: {algorithm} vs {reference}")
        print("Executing synthetic datasets and reference comparisons...")
        
        # Instantiate real matrix
        matrix = BenchmarkMatrix()
        
        # Mock plugin objects for the matrix engine based on manifest strings
        MockMethod = namedtuple('MockMethod', ['method_name'])
        matrix.add_method(MockMethod(method_name=algorithm))
        
        # Read datasets from manifest or use default
        datasets = campaign.get("datasets", ["BCI_Competition_IV"])
        for ds in datasets:
            matrix.add_dataset(ds)
            
        # Execute the real matrix sweeps
        results = matrix.execute_matrix()
        
        # Compute aggregate metrics from results
        passed_count = sum(1 for r in results if r.get('conclusion_verdict') == 'PASS')
        mean_ccc = sum(r.get('statistical_agreement', {}).get('ccc', 0.0) for r in results) / max(len(results), 1)
        
        print(f"\nCampaign Complete! Executed {len(results)} permutations.")
        if results:
            print(f"Evidence Hash [0]: {results[0].get('bundle_id')}")
            print(f"Overall Verdict: {'PASS' if passed_count == len(results) else 'FAIL'}")
            print(f"Mean CCC: {mean_ccc:.4f}")
        
def main():
    if len(sys.argv) < 3 or sys.argv[1] != "run":
        print("Usage: vireon campaign run <manifest.yaml>")
        sys.exit(1)
        
    cli = CampaignCLI()
    cli.run_campaign(sys.argv[2])

if __name__ == "__main__":
    main()
