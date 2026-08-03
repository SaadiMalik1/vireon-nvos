"""Auto-generate API reference from docstrings using mkdocstrings."""
import os

PACKAGES = [
    "vireon_core",
    "vireon_methods",
    "vireon_validation",
    "vireon_evidence",
    "vireon_models",
    "vireon_knowledge",
    "vireon_corpus",
    "vireon_api",
]


def generate():
    os.makedirs("docs/api", exist_ok=True)
    with open("docs/api_reference.md", "w", encoding="utf-8") as f:
        f.write("# VIREON API Reference\n\n")
        f.write("This document provides reference documentation for all VIREON packages.\n\n")
        for pkg in PACKAGES:
            f.write(f"## {pkg}\n\n")
            f.write(f"::: {pkg}\n\n")
            f.write(f"Comprehensive documentation and interfaces for `{pkg}`.\n\n")
    print("API reference: docs/api_reference.md")


if __name__ == "__main__":
    generate()
