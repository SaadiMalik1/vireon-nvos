"""
VIREON × MOABB — Statistics layer.

Per ADR 0008 #5: VIREON owns statistical validation beyond MOABB's scope.
Subject-level bootstrap CIs (not trial-level — avoids pseudoreplication),
permutation tests that respect experimental structure, effect sizes, and
FDR multiple-comparison correction.

All procedures operate at the SUBJECT level when given subject-level
accuracies. The bootstrap and permutation classes embed the unit ("subject")
in their result dataclasses so downstream code can verify the resampling
unit matches the experimental unit.
"""
from vireon_moabb.statistics.bootstrap import SubjectLevelBootstrap, BootstrapResult
from vireon_moabb.statistics.permutation import SubjectLevelPermutation, PermutationResult
from vireon_moabb.statistics.effect_size import CohensD, GlassDelta
from vireon_moabb.statistics.multiple_comparison import FDRCorrection

__all__ = [
    # Bootstrap
    "SubjectLevelBootstrap",
    "BootstrapResult",
    # Permutation
    "SubjectLevelPermutation",
    "PermutationResult",
    # Effect sizes
    "CohensD",
    "GlassDelta",
    # Multiple comparison
    "FDRCorrection",
]
