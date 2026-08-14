"""
VIREON × MOABB Integration
==========================

VIREON's validation and evidence layer for MOABB benchmarks.

This package implements the architecture defined in ADR 0008:
- VIREON owns experiment specification, validation, provenance, evidence
- MOABB owns BCI datasets, paradigms, pipelines, evaluation

Usage:
    from vireon_moabb import MoabbExecutor, ValidationLayer, EvidenceAssembler, Reporter

    executor = MoabbExecutor()
    traces = executor.run(spec)

    validator = ValidationLayer()
    validation = validator.validate(traces)

    assembler = EvidenceAssembler()
    bundle = assembler.assemble(traces, validation)

    reporter = Reporter()
    report = reporter.generate_raw_evidence_report(traces, validation, bundle)
    print(report)
"""
from vireon_moabb.executor import MoabbExecutor, MoabbExecutionTrace
from vireon_moabb.validation import ValidationLayer, ValidationResult
from vireon_moabb.evidence import EvidenceAssembler
from vireon_moabb.report import Reporter
from vireon_moabb.spec import (
    ExperimentSpec, DatasetSpec, ParadigmSpec, PipelineSpec, EvaluationSpec,
    StatisticsSpec, RobustnessSpec, ProvenanceSpec, quick_spec, standard_spec, research_spec,
)

__version__ = "0.1.0"
__all__ = [
    "MoabbExecutor", "MoabbExecutionTrace",
    "ValidationLayer", "ValidationResult",
    "EvidenceAssembler",
    "Reporter",
    "ExperimentSpec", "DatasetSpec", "ParadigmSpec", "PipelineSpec",
    "EvaluationSpec", "StatisticsSpec", "RobustnessSpec", "ProvenanceSpec",
    "quick_spec", "standard_spec", "research_spec",
]
