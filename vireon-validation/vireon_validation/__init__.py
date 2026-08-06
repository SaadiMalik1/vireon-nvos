"""vireon_validation main package."""
from vireon_validation.benchmarks.matrix import BenchmarkMatrix
from vireon_validation.statistics.bootstrap import bootstrap_ci
from vireon_validation.statistics.permutation import permutation_test
from vireon_validation.statistics.effect_sizes import cohens_d
from vireon_validation.statistics.multiple_comparisons import benjamini_hochberg
from vireon_validation.evidence.generator import EvidenceGenerator
from vireon_validation.metrics import generate_signal_metrics

__version__ = "1.0.2"
__all__ = [
    "BenchmarkMatrix", "bootstrap_ci", "permutation_test", "cohens_d",
    "benjamini_hochberg", "EvidenceGenerator", "generate_signal_metrics"
]
