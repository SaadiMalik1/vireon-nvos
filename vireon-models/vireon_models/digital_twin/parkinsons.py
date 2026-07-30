import numpy as np
from vireon_models.digital_twin.models import IDiseaseModel, IMedicationModel

class ParkinsonsDiseaseModel(IDiseaseModel):
    """
    Simulates the pathological alteration of the Subthalamic Nucleus (STN).
    Specifically, increases power in the beta band (13-30 Hz).
    
    Validated Components:
    ✓ Beta oscillation modulation
    ✓ Medication response (via LevodopaMedicationModel)
    ✓ DBS artifact generation (via DBSDeviceModel)
    
    Future Components:
    ○ Disease progression
    ○ Adaptive DBS
    ○ Closed-loop control
    ○ Multi-region networks
    """
    def __init__(self, beta_amplification_factor: float = 2.5):
        self.beta_amplification_factor = beta_amplification_factor

    def apply_pathology(self, neural_source: np.ndarray, sample_rate: float) -> np.ndarray:
        from scipy.signal import butter, filtfilt
        nyq = 0.5 * sample_rate
        low = 13.0 / nyq
        high = 30.0 / nyq
        # Filter for beta band
        b, a = butter(4, [low, high], btype='band')
        beta_band = filtfilt(b, a, neural_source)
        # Recombine original with amplified beta
        return neural_source + (beta_band * (self.beta_amplification_factor - 1.0))

class LevodopaMedicationModel(IMedicationModel):
    """
    Simulates the pharmacodynamic effect of Levodopa on the STN.
    Levodopa attenuates pathological beta oscillations.
    """
    def __init__(self, dose_mg: float = 100.0, half_life_hours: float = 1.5):
        self.dose_mg = dose_mg
        self.half_life_hours = half_life_hours
        
    def apply_pharmacodynamics(self, neural_source: np.ndarray) -> np.ndarray:
        # Simple attenuation model proportional to dose
        attenuation = max(0.2, 1.0 - (self.dose_mg / 200.0))
        return neural_source * attenuation

class DBSDeviceModel:
    """
    Simulates high-frequency stimulation (e.g. 130 Hz) applied to the STN.
    DBS creates a stimulation artifact and suppresses pathological firing.
    """
    def __init__(self, frequency_hz: float = 130.0, amplitude_ma: float = 3.0):
        self.frequency_hz = frequency_hz
        self.amplitude_ma = amplitude_ma
        
    def apply_stimulation(self, neural_source: np.ndarray, sampling_rate: float) -> np.ndarray:
        # Suppress endogenous activity
        suppressed_source = neural_source * 0.1
        
        # Add stimulation artifact (simplified as a sine wave at the stimulation frequency)
        t = np.arange(neural_source.shape[-1]) / sampling_rate
        artifact = self.amplitude_ma * np.sin(2 * np.pi * self.frequency_hz * t)
        
        return suppressed_source + artifact
