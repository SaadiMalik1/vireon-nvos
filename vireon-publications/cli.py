import argparse

def main():
    parser = argparse.ArgumentParser(description="VIREON Publications CLI")
    parser.add_argument("command", choices=["reproduce"])
    parser.add_argument("doi", help="The DOI of the paper to reproduce, e.g., 10.1038/s41597-020-00650-8")
    
    args = parser.parse_args()
    
    if args.command == "reproduce":
        import os
        from vireon_lab.cli.reproduce import ReproducibilityEngine
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        workspace_root = os.path.abspath(os.path.join(base_dir, ".."))
        engine = ReproducibilityEngine(workspace_root)
        engine.reproduce_doi(args.doi)

if __name__ == "__main__":
    main()
