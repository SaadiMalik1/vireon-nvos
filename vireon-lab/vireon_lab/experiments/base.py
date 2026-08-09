from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from vireon_core.contracts import IExperimentDef, IProvider, IStimulus, IAssertion

class ExperimentSchema(BaseModel):
    """
    Base Pydantic schema for all YAML experiments.
    """
    id: str
    classification: Dict[str, str]
    system: Dict[str, Any]  # Widened to allow nested config dicts
    stimulus: Optional[Dict[str, Any]] = None
    perturbation: Optional[Dict[str, Any]] = None
    expected: Dict[str, Any]
    measurements: List[str]
    evidence: List[str]
    regulatory: Optional[Dict[str, Any]] = None


def _build_provider(system_config: Dict[str, Any]) -> IProvider:
    """
    Factory that selects the correct IProvider based on the YAML system.provider field.
    """
    provider_name = system_config.get("provider", "mock_provider")
    config = system_config.get("config", {})

    if provider_name == "synthetic_eeg":
        from vireon_models.providers.datasets import SyntheticSignalProvider
        return SyntheticSignalProvider(**config)
    elif provider_name == "motor_imagery":
        from vireon_models.providers.datasets import MotorImageryProvider
        return MotorImageryProvider(**config)
    elif provider_name == "bci_competition_iv":
        from vireon_models.providers.datasets import SyntheticMotorImageryProvider
        return SyntheticMotorImageryProvider(**config)
    elif provider_name == "mne":
        from vireon_models.providers.mne_provider import MNEProvider
        return MNEProvider(**config)
    elif provider_name == "eegbci":
        from vireon_models.providers.eegbci_provider import EEGBCIProvider
        return EEGBCIProvider(**config)
    elif provider_name == "physionet_mi":
        from vireon_models.providers.datasets import PhysioNetMotorImageryProvider
        return PhysioNetMotorImageryProvider(**config)
    else:
        # Default: MockProvider for backward compatibility
        from vireon_lab.experiments.schema import MockProvider
        return MockProvider()


class BaseExperiment(IExperimentDef):
    """
    Base implementation for all experiment types.
    """
    def __init__(self, schema: ExperimentSchema):
        self.schema = schema

    def get_provider(self) -> IProvider:
        return _build_provider(self.schema.system)

    def get_stimulus(self) -> List[IStimulus]:
        stimuli = []
        if self.schema.stimulus:
            stimuli.append(IStimulus(type="intended_action", parameters=self.schema.stimulus))
        if self.schema.perturbation:
            stimuli.append(IStimulus(type="perturbation", parameters=self.schema.perturbation))
        return stimuli

    def get_assertions(self) -> List[IAssertion]:
        assertions = []
        for key, value in self.schema.expected.items():
            assertions.append(IAssertion(
                name=f"expected_{key}",
                description=f"Expect {key} to be {value}",
                expected_result=value
            ))
        return assertions

