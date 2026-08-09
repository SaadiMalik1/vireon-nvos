import argparse
import sys
from vireon_simple.api import inspect, validate, report
from vireon_simple.tui import plan_interactive

def main():
    parser = argparse.ArgumentParser(description="VIREON — Scientific validation for neurotechnology.")
    subparsers = parser.add_subparsers(dest="command")

    # Inspect
    inspect_parser = subparsers.add_parser("inspect", help="Inspect a dataset")
    inspect_parser.add_argument("file", help="File path or dataset key")

    # Validate
    validate_parser = subparsers.add_parser("validate", help="Run validation")
    validate_parser.add_argument("file", help="File path or dataset key")
    validate_parser.add_argument("--method", default="csp_lda", help="Algorithm short name")
    validate_parser.add_argument("--quick", action="store_true", help="Quick mode")
    validate_parser.add_argument("--standard", action="store_true", help="Standard mode")
    validate_parser.add_argument("--research", action="store_true", help="Research mode")

    # Report
    report_parser = subparsers.add_parser("report", help="View a stored result")
    report_parser.add_argument("hash", help="Evidence hash")

    # Plan
    plan_parser = subparsers.add_parser("plan", help="Interactively build a validation plan")

    args = parser.parse_args()

    if args.command == "inspect":
        info = inspect(args.file)
        print(info.summary())
    elif args.command == "validate":
        mode = "standard"
        if args.quick: mode = "quick"
        elif args.research: mode = "research"
        elif args.standard: mode = "standard"
        
        result = validate(args.file, method=args.method, mode=mode)
        print(report(result))
    elif args.command == "report":
        # Mock fetch from hash for CLI demo
        print(f"Report for hash {args.hash}")
    elif args.command == "plan":
        plan_interactive()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
