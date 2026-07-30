import numpy as np
from typing import Dict, Any, List, Optional

class BrainNetwork:
    """
    Models the source-space neural activity before volume conduction.
    Generates signals for abstract anatomical nodes (e.g., visual cortex, motor cortex).
    """
    def __init__(self, num_nodes: int = 4, seed: int = 42):
        self.num_nodes = num_nodes
        self.rng = np.random.default_rng(seed)

    def generate_source_activity(self, num_samples: int, sample_rate: float) -> np.ndarray:
        """
        Generates source-level neural mass activity (1/f background + oscillations).
        Returns shape (num_samples, num_nodes)
        """
        t = np.linspace(0, num_samples / sample_rate, num_samples, endpoint=False)
        
        # 1/f background per node
        white_noise = self.rng.standard_normal((num_samples, self.num_nodes)).astype(np.float32)
        fft = np.fft.rfft(white_noise, axis=0)
        freqs = np.fft.rfftfreq(num_samples)
        freqs[0] = 1.0
        fft_pink = fft / (np.sqrt(freqs)[:, None])
        sources = np.fft.irfft(fft_pink, n=num_samples, axis=0).astype(np.float32) * 5.0
        
        # Add a specific state-dependent oscillation to node 0 (e.g., Motor Cortex Mu rhythm)
        sources[:, 0] += np.sin(2 * np.pi * 10.0 * t) * 10.0
        
        # Add specific oscillation to node 1 (e.g., Visual Cortex Alpha rhythm)
        sources[:, 1] += np.sin(2 * np.pi * 11.5 * t) * 12.0

        return sources

class DiseaseModel:
    """
    Models pathological perturbations to the brain network.
    """
    def __init__(self, name: str, severity: float = 1.0):
        self.name = name
        self.severity = severity
        
    def apply(self, sources: np.ndarray, sample_rate: float) -> np.ndarray:
        if self.name == "epilepsy":
            # Add hypersynchronous high-frequency oscillations (HFOs)
            t = np.linspace(0, sources.shape[0] / sample_rate, sources.shape[0], endpoint=False)
            hfo = np.sin(2 * np.pi * 80.0 * t) * (20.0 * self.severity)
            sources[:, 0] += hfo  # Focal onset in node 0
        return sources

class MedicationModel:
    """
    Models therapeutic interventions that dampen disease effects.
    """
    def __init__(self, name: str, dose: float = 1.0):
        self.name = name
        self.dose = dose
        
    def apply(self, sources: np.ndarray, sample_rate: float) -> np.ndarray:
        if self.name == "levetiracetam":
            # Simple dampening of high frequency energy
            # In a real model, this would be a pharmacological kinetic filter
            fft = np.fft.rfft(sources, axis=0)
            freqs = np.fft.rfftfreq(sources.shape[0], d=1.0/sample_rate)
            # Attenuate frequencies above 30Hz
            mask = freqs > 30.0
            fft[mask, :] *= max(0.0, 1.0 - (0.5 * self.dose))
            sources = np.fft.irfft(fft, n=sources.shape[0], axis=0).astype(np.float32)
        return sources

class DigitalPatient:
    """
    Represents the biological characteristics of the digital twin.
    """
    def __init__(self, age: int, disease: Optional[DiseaseModel] = None, medication: Optional[MedicationModel] = None, seed: int = 42):
        self.age = age
        self.disease = disease
        self.medication = medication
        self.brain = BrainNetwork(num_nodes=4, seed=seed)
        
    def generate_brain_activity(self, duration_sec: float, sample_rate: float) -> np.ndarray:
        num_samples = int(duration_sec * sample_rate)
        sources = self.brain.generate_source_activity(num_samples, sample_rate)
        
        if self.disease:
            sources = self.disease.apply(sources, sample_rate)
            
        if self.medication:
            sources = self.medication.apply(sources, sample_rate)
            
        return sources
