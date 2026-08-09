HUMAN_TERMS = {
    "EvidenceQualityEngine": "How trustworthy is this result?",
    "MethodologicalValidator": "Does the experiment follow sound scientific methodology?",
    "ScientificReproducibilityIndex": "Could another researcher reproduce this result?",
    "IUncertainty": "How certain is this result?",
    "EvidenceBundle": "Cryptographic evidence record",
    "EvidenceGraph": "Provenance history",
    "KnowledgeGraph": "Scientific assumptions database",
    "DatasetProvider": "Dataset loader",
    "MethodPlugin": "Algorithm",
    "ValidationSpec": "Validation plan",
    "StatisticsSpec": "Statistical analysis",
    "RobustnessSpec": "Stress testing",
    "ReferenceSpec": "Comparison to reference implementation",
    "ProvenanceSpec": "Audit trail",
    "EnvironmentFingerprint": "Execution environment",
    "ExecutionEngine": "VIREON engine",
    "ContractValidator": "Scientific assumption checker",
    "ScientificContractViolation": "Scientific assumption violated",
    "LinConcordanceCorrelation": "Agreement with reference",
    "BootstrapCI": "Confidence interval",
    "PermutationTest": "Significance test",
}

def humanize(term: str) -> str:
    """Translate an internal term to a human-readable phrase."""
    return HUMAN_TERMS.get(term, term)

def humanize_dict(d: dict) -> dict:
    """Recursively translate keys in a dict."""
    return {humanize(k): v if not isinstance(v, dict) else humanize_dict(v) for k, v in d.items()}
