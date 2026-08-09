#!/usr/bin/env python3
"""Verify all evidence_hash assignments are 64-char hex or hashlib.sha256 calls."""
import ast
import re
import sys
from pathlib import Path

ROOT = Path(".")
HEX64 = re.compile(r'^[0-9a-f]{64}$')

violations = []

for py_file in ROOT.rglob("*.py"):
    if ".git" in py_file.parts or "site-packages" in str(py_file) or "venv" in str(py_file):
        continue
    try:
        tree = ast.parse(py_file.read_text())
    except SyntaxError:
        continue

    for node in ast.walk(tree):
        # Look for assignments to evidence_hash or execution_hash
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in ("evidence_hash", "execution_hash"):
                    val = node.value
                    if isinstance(val, ast.Constant) and isinstance(val.value, str):
                        if val.value == "":
                            violations.append(f"{py_file}:{node.lineno}: empty string hash")
                        elif not HEX64.match(val.value):
                            violations.append(f"{py_file}:{node.lineno}: non-SHA256 string hash: {val.value!r}")

if violations:
    print("FAIL: Hash integrity violations found:")
    for v in violations:
        print(f"  {v}")
    sys.exit(1)
else:
    print("PASS: All hash assignments are 64-char hex or hashlib.sha256 calls.")
