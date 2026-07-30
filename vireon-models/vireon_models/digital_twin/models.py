from abc import ABC, abstractmethod
from typing import Any, Dict
from pydantic import BaseModel
import numpy as np

class IPatientModel(ABC):
    @abstractmethod
    def get_baseline_physiology(self) -> Dict[str, Any]:
        pass

class IDiseaseModel(ABC):
    @abstractmethod
    def apply_pathology(self, neural_source: np.ndarray, sample_rate: float) -> np.ndarray:
        pass

class IMedicationModel(ABC):
    @abstractmethod
    def apply_pharmacodynamics(self, neural_source: np.ndarray) -> np.ndarray:
        pass

class DigitalTwinPipeline:
    """
    Simulates the causal chain: Patient -> Disease -> Medication -> Neural Tissue
    """
    def __init__(self, patient: IPatientModel, disease: IDiseaseModel, medication: IMedicationModel):
        self.patient = patient
        self.disease = disease
        self.medication = medication

    def generate_tissue_activity(self, base_activity: np.ndarray, sample_rate: float) -> np.ndarray:
        activity = self.disease.apply_pathology(base_activity, sample_rate)
        activity = self.medication.apply_pharmacodynamics(activity)
        return activity
