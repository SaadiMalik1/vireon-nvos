"""vireon_corpus main package."""
from vireon_corpus.dataset_manager import DatasetManager
from vireon_corpus.exceptions import (
    VireonCorpusError,
    UnknownDatasetError,
    DatasetDownloadError,
    DatasetValidationError,
)

__version__ = "1.1.0"
__all__ = [
    "DatasetManager",
    "VireonCorpusError",
    "UnknownDatasetError",
    "DatasetDownloadError",
    "DatasetValidationError",
]
