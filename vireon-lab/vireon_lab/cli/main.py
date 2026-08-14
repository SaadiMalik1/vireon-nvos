import argparse
import sys
import json
from vireon_moabb.spec import standard_spec
from vireon_moabb.executor import MoabbExecutor
from vireon_moabb.evidence import EvidenceAssembler
from vireon_moabb.report import Reporter
from vireon_moabb.validation import ValidationLayer

def validate_command(args):
    print(f"Running validation on dataset: {args.dataset} with pipeline: {args.pipeline}")
    spec = standard_spec(dataset=args.dataset, subject=args.subject, pipeline_name=args.pipeline)
    trace = MoabbExecutor().run(spec)
    validation = ValidationLayer().validate(trace, spec)
    bundle = EvidenceAssembler().assemble(spec.model_dump(), trace, validation)
    report = Reporter().generate_scorecard(bundle)
    print(report)

def inspect_command(args):
    print(f"Inspecting bundle: {args.bundle_id}")

def main():
    parser = argparse.ArgumentParser(description="VIREON Laboratory CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Run validation pipeline")
    validate_parser.add_argument("dataset", nargs="?", default="BNCI2014_001", help="Dataset name")
    validate_parser.add_argument("--pipeline", default="logvar_lda", help="Pipeline name")
    validate_parser.add_argument("--mode", default="standard", help="Execution mode")
    validate_parser.add_argument("--subject", type=int, help="Specific subject ID")

    inspect_parser = subparsers.add_parser("inspect", help="Inspect an evidence bundle")
    inspect_parser.add_argument("bundle_id", help="Evidence bundle ID")

    args = parser.parse_args()

    if args.command == "validate":
        validate_command(args)
    elif args.command == "inspect":
        inspect_command(args)

if __name__ == "__main__":
    main()
