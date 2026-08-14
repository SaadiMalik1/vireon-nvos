"""VIREON Corpus exceptions.

Added in playbook dx — used by fixed DatasetManager.load_dataset().
"""


class VireonCorpusError(Exception):
    """Base exception for vireon-corpus."""


class UnknownDatasetError(VireonCorpusError):
    """Raised when an unknown dataset key is requested."""


class DatasetDownloadError(VireonCorpusError):
    """Raised when a dataset download fails and no fallback is available."""


class DatasetValidationError(VireonCorpusError):
    """Raised when downloaded data fails checksum or shape validation."""
