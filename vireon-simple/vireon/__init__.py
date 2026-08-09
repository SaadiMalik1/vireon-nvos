"""VIREON — Scientific validation for neurotechnology.

Simple API:
    import vireon
    result = vireon.validate("data.edf", method="csp_lda")
    result.report()

    info = vireon.inspect("data.edf")
    print(info.summary())

Advanced API:
    from vireon_core.specs import ExperimentSpec, quick_spec, standard_spec, research_spec
    spec = standard_spec("data.edf", "csp", goal="Determine if CSP-LDA generalizes")
    result = vireon.run(spec)
"""
from vireon_simple.api import validate, inspect, run, report, reproduce, verify
from vireon_simple.api import DatasetInspection, ExperimentResult

__version__ = "1.1.0"
__all__ = ["validate", "inspect", "run", "report", "reproduce", "verify", "DatasetInspection", "ExperimentResult"]
