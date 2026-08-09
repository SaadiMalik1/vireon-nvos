#!/usr/bin/env python3
"""Sync all subpackage __version__ strings to 1.1.0."""
import re
from pathlib import Path

def main():
    root = Path(".")
    changed = 0
    pattern = re.compile(r'^__version__\s*=\s*["\'].*?["\']', re.MULTILINE)
    
    for init_file in root.glob("vireon-*/**/__init__.py"):
        content = init_file.read_text()
        if pattern.search(content):
            new_content = pattern.sub('__version__ = "1.1.0"', content)
            if new_content != content:
                init_file.write_text(new_content)
                changed += 1
                print(f"Updated {init_file}")

    print(f"Synced {changed} __init__.py files to 1.1.0")

if __name__ == "__main__":
    main()
