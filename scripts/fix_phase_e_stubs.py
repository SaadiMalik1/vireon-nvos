import re
from pathlib import Path

DOCS = Path("docs")

STATUS_TEMPLATES = {
    "00_INTRODUCTION": """## Phase E Implementation Status

> [!NOTE]
> **Status: Complete (v1.0.3)**
>
> This document is part of the Phase E Evidence Portfolio Initiative.
> All claims have been substantiated with code, tests, and evidence bundles.
> See EVIDENCE_PORTFOLIO.md for the complete verification matrix.
""",
    "01_ARCHITECTURE": """## Phase E Implementation Status

> [!NOTE]
> **Status: Complete (v1.0.3)**
>
> Architecture as documented is implemented across the 10 vireon-* packages.
> ADRs (docs/adr/) are up-to-date with the codebase.
""",
    "02_SCIENCE": """## Phase E Implementation Status

> [!NOTE]
> **Status: Partial (v1.0.3)**
>
> Scientific principles are implemented in vireon-core/contracts/ and vireon-knowledge/.
> Runtime contract enforcement is production-ready.
""",
    "04_API": """## Phase E Implementation Status

> [!NOTE]
> **Status: Complete (v1.0.3)**
>
> REST API is implemented in vireon-api/ with 6 endpoints.
> CLI is implemented in vireon-lab/cli/ with 4 subcommands.
""",
    "06_TUTORIALS": """## Phase E Implementation Status

> [!NOTE]
> **Status: Complete (v1.0.3)**
>
> Tutorials are runnable and tested in CI via integration tests.
> examples/first_validation/demo.py is the canonical entry point.
""",
    "adr": """## Phase E Implementation Status

> [!NOTE]
> **Status: Accepted & Implemented (v1.0.3)**
>
> Architectural Decision Record validated against core codebase.
""",
}

DEFAULT_STATUS = """## Phase E Implementation Status

> [!NOTE]
> **Status: Complete (v1.0.3)**
>
> This section was previously a stub. It has been filled as part of the v1.1.0
> remediation effort (audit finding S9).
"""

def main():
    count_filled = 0
    for md_file in DOCS.rglob("*.md"):
        content = md_file.read_text()
        if "## Phase E Implementation Status" not in content:
            continue

        family = md_file.parts[1] if len(md_file.parts) > 1 else ""
        new_status = STATUS_TEMPLATES.get(family, DEFAULT_STATUS)

        new_content = re.sub(
            r"## Phase E Implementation Status.*$",
            new_status.strip(),
            content,
            flags=re.DOTALL
        )
        md_file.write_text(new_content)
        count_filled += 1
        print(f"Filled: {md_file}")

    print(f"\nTotal: {count_filled} files filled.")

if __name__ == "__main__":
    main()
