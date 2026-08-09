"""Exceptions for vireon-evidence registry and verification."""


class VireonEvidenceError(Exception):
    """Base exception for vireon-evidence."""


class EvidenceAlreadyRegisteredError(VireonEvidenceError):
    """Raised when attempting to register a bundle whose hash already exists with different content."""


class EvidenceTamperError(VireonEvidenceError):
    """Raised when bundle integrity verification fails."""
