import argparse
import sys
import os

from vireon_lab.cli.dataset_manager import fetch_dataset, get_available_datasets
from vireon_lab.cli.runner import ExperimentRunner

def main():
    parser = argparse.ArgumentParser(description="VIREON Command Line Interface")
    
    subparsers = parser.add_subparsers(dest="command")
    
    dataset_parser = subparsers.add_parser("dataset", help="Manage datasets")
    dataset_parser.add_argument("dataset_cmd", choices=["list", "fetch"], help="List or fetch datasets")
    dataset_parser.add_argument("--name", type=str, help="Name of the dataset to fetch")
    
    experiment_parser = subparsers.add_parser("experiment", help="Run experiments via the Evidence Generation Engine")
    experiment_parser.add_argument("experiment_cmd", choices=["run"], help="Run experiments")
    experiment_parser.add_argument("--campaign", type=str, default="all", help="Campaign name or specific experiment id to run (default: all)")
    experiment_parser.add_argument("--repetitions", type=int, default=1, help="Number of repetitions per experiment")
    experiment_parser.add_argument("--gpu", action="store_true", default=True, help="Use GPU hardware acceleration if available (default: True)")
    experiment_parser.add_argument("--no-gpu", action="store_false", dest="gpu", help="Disable GPU hardware acceleration")
    
    verify_parser = subparsers.add_parser("verify", help="Verify reproducibility bundle integrity")
    verify_parser.add_argument("--bundle", type=str, required=True, help="Path to the evidence bundle directory")
    
    reproduce_parser = subparsers.add_parser("reproduce", help="Reproduce a publication")
    reproduce_parser.add_argument("doi", type=str, help="The DOI of the publication to reproduce (e.g. doi:10.1234/vireon.1)")

    args = parser.parse_args()
    
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    if args.command == "dataset":
        if args.dataset_cmd == "list":
            datasets = get_available_datasets()
            print("Available Datasets:")
            for d in datasets:
                print(f"- {d}")
        elif args.dataset_cmd == "fetch":
            if not args.name:
                print("Error: --name is required for fetch command")
                sys.exit(1)
            out_dir = os.path.join(base_dir, "vireon-benchmarks", "datasets")
            os.makedirs(out_dir, exist_ok=True)
            fetch_dataset(args.name, out_dir)
                
    elif args.command == "experiment":
        if args.experiment_cmd == "run":
            # __file__ is vireon-lab/vireon_lab/cli/main.py, so base_dir is vireon-lab
            experiments_dir = os.path.join(base_dir, "vireon_lab", "experiments")
            results_dir = os.path.join(base_dir, "..", "results") # store results in VIREON/results
            
            runner = ExperimentRunner(
                experiments_dir=experiments_dir,
                results_dir=results_dir,
                repetitions=args.repetitions
            )
            runner.run_campaign(args.campaign)
            
    elif args.command == "verify":
        from vireon_lab.replay import ReplayEngine
        engine = ReplayEngine()
        result = engine.verify_bundle_integrity(args.bundle)
        if result.get("valid", False):
            print(f"[OK] Bundle {args.bundle} verified. All hashes match.")
            sys.exit(0)
        else:
            print(f"[FAIL] Bundle {args.bundle} verification failed:")
            for mismatch_file, mismatch_info in (result.get("mismatches") or {}).items():
                print(f"  - {mismatch_file}: {mismatch_info['actual']} != {mismatch_info['expected']}")
            sys.exit(1)
            
    elif args.command == "reproduce":
        from vireon_lab.cli.reproduce import ReproducibilityEngine
        workspace_root = os.path.abspath(os.path.join(base_dir, ".."))
        engine = ReproducibilityEngine(workspace_root)
        engine.reproduce_doi(args.doi)

if __name__ == "__main__":
    main()
