import sys
import re

def verify_tutorial(filepath):
    print(f"Verifying {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    pattern = r"```python\s*\n(.*?)```"
    blocks = re.findall(pattern, text, re.DOTALL)
    if not blocks:
        print(f"No python blocks found in {filepath}")
        return
        
    for i, block in enumerate(blocks, 1):
        print(f"--- Executing Block {i} ---")
        global_vars = {}
        exec(block, global_vars)
    print(f"PASS: {filepath}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/verify_tutorial.py <path_to_md>")
        sys.exit(1)
    verify_tutorial(sys.argv[1])
