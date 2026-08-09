#!/usr/bin/env python3
"""Auto-generate API reference from actual module signatures."""
import importlib
import inspect
import sys
import os
from pathlib import Path

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for pkg in ["vireon-core", "vireon-models", "vireon-methods", "vireon-validation", "vireon-evidence", "vireon-knowledge", "vireon-corpus", "vireon-api"]:
    pkg_path = os.path.join(repo_root, pkg)
    if pkg_path not in sys.path:
        sys.path.insert(0, pkg_path)

MODULES = [
    "vireon_methods.spectral.vireon_welch",
    "vireon_methods.spectral.vireon_fft",
    "vireon_methods.spectral.vireon_stft",
    "vireon_methods.spectral.vireon_wavelets",
    "vireon_methods.spectral.vireon_multitaper",
    "vireon_methods.spatial.vireon_csp",
    "vireon_methods.spatial.vireon_ica",
    "vireon_methods.spatial.vireon_fbcsp",
    "vireon_methods.spatial.vireon_xdawn",
    "vireon_methods.spatial.vireon_riemannian",
    "vireon_methods.filtering.vireon_iir",
    "vireon_methods.filtering.vireon_fir",
    "vireon_methods.connectivity.vireon_connectivity",
    "vireon_methods.connectivity.vireon_mutual_information",
    "vireon_methods.deep_learning.eegnet",
    "vireon_methods.deep_learning.deepconvnet",
    "vireon_core.contracts.evidence",
    "vireon_core.contracts.plugin",
    "vireon_evidence.registry.core",
    "vireon_evidence.graph.core",
    "vireon_corpus.dataset_manager",
    "vireon_knowledge.engine",
]

def main():
    out = ["# VIREON API Reference\n"]
    out.append("Auto-generated from source.\n")
    out.append("---\n")

    for mod_name in MODULES:
        try:
            mod = importlib.import_module(mod_name)
        except ImportError as e:
            out.append(f"\n## `{mod_name}`\n\n*Import failed: {e}*\n")
            continue

        out.append(f"\n## `{mod_name}`\n")
        if mod.__doc__:
            out.append(f"\n{mod.__doc__}\n")

        for name, obj in inspect.getmembers(mod, inspect.isclass):
            if obj.__module__ != mod_name:
                continue
            out.append(f"\n### `{name}`\n")
            if obj.__doc__:
                out.append(f"\n{obj.__doc__}\n")
            try:
                sig = inspect.signature(obj.__init__)
                out.append(f"\n```python\n{name}{sig}\n```\n")
            except (ValueError, TypeError):
                pass

    os.makedirs("docs", exist_ok=True)
    Path("docs/api_reference.md").write_text("\n".join(out))
    print(f"Generated docs/api_reference.md ({len(out)} sections)")

if __name__ == "__main__":
    main()
