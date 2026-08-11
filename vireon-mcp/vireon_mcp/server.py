class McpServer:
    """Mock MCP server for VIREON."""

    def __init__(self):
        self.tools = [
            "run_moabb_benchmark",
            "get_evidence_bundle",
            "verify_evidence_integrity",
            "list_supported_datasets",
            "list_supported_paradigms",
            "get_compliance_scorecard"
        ]

    def register_tools(self):
        pass

    def run(self):
        pass
