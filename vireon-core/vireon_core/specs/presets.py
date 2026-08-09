from vireon_core.specs.experiment import (
    ExperimentSpec,
    DatasetSpec,
    MethodSpec,
    ValidationSpec,
    StatisticsSpec,
    ProvenanceSpec,
    PreprocessingSpec,
    RobustnessSpec,
    PerturbationSpec,
    ReferenceSpec
)


def quick_spec(dataset: str, method: str, goal: str = "") -> ExperimentSpec:
    return ExperimentSpec(
        name=f"Quick validation: {method}",
        goal=goal or f"Quick validation of {method} on {dataset}",
        mode="quick",
        dataset=DatasetSpec(source=dataset),
        method=MethodSpec(algorithm=method),
        validation=ValidationSpec(strategy="single_run"),
        statistics=StatisticsSpec(metrics=["accuracy"], significance_test=None, confidence_interval=None),
        provenance=ProvenanceSpec(record=True, evidence_bundle=False),
    )


def standard_spec(dataset: str, method: str, goal: str = "") -> ExperimentSpec:
    return ExperimentSpec(
        name=f"Standard validation: {method}",
        goal=goal or f"Standard validation of {method} on {dataset}",
        mode="standard",
        dataset=DatasetSpec(source=dataset),
        preprocessing=[PreprocessingSpec(type="filter", parameters={"kind": "bandpass", "low": 8, "high": 30})],
        method=MethodSpec(algorithm=method, decoder="lda"),
        validation=ValidationSpec(strategy="k_fold", k=5),
        statistics=StatisticsSpec(
            metrics=["accuracy", "balanced_accuracy"],
            significance_test="permutation",
            confidence_interval="bootstrap",
        ),
    )


def research_spec(dataset: str, method: str, goal: str = "") -> ExperimentSpec:
    return ExperimentSpec(
        name=f"Research validation: {method}",
        goal=goal or f"Full scientific validation of {method} on {dataset}",
        mode="research",
        dataset=DatasetSpec(source=dataset),
        preprocessing=[PreprocessingSpec(type="filter", parameters={"kind": "bandpass", "low": 8, "high": 30})],
        method=MethodSpec(algorithm=method, decoder="lda"),
        validation=ValidationSpec(strategy="k_fold", k=5),
        statistics=StatisticsSpec(
            metrics=["accuracy", "balanced_accuracy", "cohen_kappa"],
            significance_test="permutation",
            n_permutations=1000,
            confidence_interval="bootstrap",
            n_bootstrap=1000,
        ),
        robustness=RobustnessSpec(perturbations=[
            PerturbationSpec(type="white_noise", severity=0.1),
            PerturbationSpec(type="channel_dropout", severity=0.2),
            PerturbationSpec(type="line_noise", severity=0.05),
        ]),
        reference=ReferenceSpec(library="scipy", function="auto", agreement_threshold=0.99),
        provenance=ProvenanceSpec(record=True, evidence_bundle=True, environment_fingerprint=True),
    )
