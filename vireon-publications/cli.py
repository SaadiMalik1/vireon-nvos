import argparse

def main():
    parser = argparse.ArgumentParser(description="VIREON Publications CLI")
    parser.add_argument("command", choices=["reproduce"])
    parser.add_argument("doi", help="The DOI of the paper to reproduce, e.g., 10.1038/s41597-020-00650-8")
    
    args = parser.parse_args()
    
    if args.command == "reproduce":
        print(f"Resolving DOI {args.doi}...")
        print("Error: Replication environment not found in local index. Ensure you have the corresponding vireon-corpus dataset downloaded.")

if __name__ == "__main__":
    main()
