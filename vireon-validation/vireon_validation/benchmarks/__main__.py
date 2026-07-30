import argparse
import sys
import os

from vireon_validation.benchmarks.runner import BenchmarkRunner
from vireon_validation.benchmarks.reporter import BenchmarkReporter

def main():
    parser = argparse.ArgumentParser(description="VIREON Benchmark Suite Runner")
    parser.add_argument(
        "--scenarios-dir", 
        type=str, 
        required=True, 
        help="Directory containing scenario YAML files"
    )
    parser.add_argument(
        "--output-dir", 
        type=str, 
        required=True, 
        help="Directory where evidence bundles and reports will be saved"
    )
    parser.add_argument(
        "--seed", 
        type=int, 
        default=42, 
        help="Global random seed for reproducible execution"
    )

    args = parser.parse_args()

    if not os.path.isdir(args.scenarios_dir):
        print(f"Error: Scenarios directory '{args.scenarios_dir}' does not exist.")
        sys.exit(1)

    print(f"Starting VIREON Benchmark Suite...")
    print(f"Scenarios Dir : {args.scenarios_dir}")
    print(f"Output Dir    : {args.output_dir}")
    print(f"Global Seed   : {args.seed}")
    print("-" * 50)

    runner = BenchmarkRunner(args.scenarios_dir, args.output_dir, seed=args.seed)
    report_data = runner.run_all()
    
    reporter = BenchmarkReporter(report_data, args.output_dir)
    md_path = reporter.generate_markdown()

    summary = report_data["summary"]
    print(f"Finished {summary['total_run']} benchmarks.")
    print(f"Passed: {summary['passed']} | Failed: {summary['failed']}")
    print(f"VIREON Validation Score: {summary['score']:.1f}%")
    print("-" * 50)
    print(f"JSON Report : {os.path.join(args.output_dir, 'benchmark_report.json')}")
    print(f"MD Report   : {md_path}")

if __name__ == "__main__":
    main()
