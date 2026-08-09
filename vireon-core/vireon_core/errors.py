class DatasetDownloadError(Exception):
    pass

class ScientificContractViolation(Exception):
    pass

class EvidenceAlreadyRegisteredError(Exception):
    pass

HUMAN_ERRORS = {
    DatasetDownloadError: {
        "title": "VIREON couldn't load your dataset",
        "causes": [
            "File format isn't supported",
            "File path is incorrect",
            "Dataset contains no EEG channels",
            "Network issue downloading remote dataset",
        ],
        "suggestions": [
            "Run `vireon inspect <file>` to verify the data",
            "Check that the file path is correct",
            "For remote datasets, check your internet connection",
        ],
    },
    ScientificContractViolation: {
        "title": "VIREON stopped because a scientific assumption was violated",
        "causes": [
            "Signal contains NaN or Inf values",
            "Signal is too short for the chosen method",
            "Signal is non-stationary but a stationary method was selected",
        ],
        "suggestions": [
            "Run `vireon inspect <file>` to see signal quality",
            "Try a different method (e.g., wavelets for non-stationary signals)",
            "Preprocess the data to remove artifacts",
        ],
    },
    EvidenceAlreadyRegisteredError: {
        "title": "VIREON detected possible evidence tampering",
        "causes": [
            "An evidence bundle with this hash was already registered with different content",
            "This may indicate a hash collision (extremely unlikely) or tampering",
        ],
        "suggestions": [
            "Use `vireon verify <hash>` to inspect the existing bundle",
            "If you need to update evidence, use `vireon update <hash> --reason <text>`",
        ],
    },
}

def translate_error(exc: Exception) -> dict:
    """Translate an exception into a human-friendly error dict."""
    for exc_type, template in HUMAN_ERRORS.items():
        if isinstance(exc, exc_type):
            return {
                "title": template["title"],
                "causes": template["causes"],
                "suggestions": template["suggestions"],
                "technical": f"{type(exc).__name__}: {exc}",
            }
    # Default
    return {
        "title": "VIREON encountered an unexpected error",
        "causes": ["Unknown cause"],
        "suggestions": ["Run with --verbose for technical details", "Report this issue on GitHub"],
        "technical": f"{type(exc).__name__}: {exc}",
    }
