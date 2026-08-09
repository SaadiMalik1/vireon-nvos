#!/usr/bin/env python3
"""Regenerate the seed evidence registry DB from seed_registry.py logic."""
import sys
import os

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for pkg in ["vireon-core", "vireon-evidence"]:
    pkg_path = os.path.join(repo_root, pkg)
    if pkg_path not in sys.path:
        sys.path.insert(0, pkg_path)

from vireon_evidence.registry.seed_registry import seed_evidence_registry

seed_evidence_registry()
print("Seed registry regenerated: evidence_registry.db")
