from abc import ABC, abstractmethod
from typing import Any, List, Optional, Dict, Type
import numpy as np
from pydantic import BaseModel
from vireon_core.contracts.base import IUncertainty, IScientificObject, ISignal, SignalType
from vireon_core.contracts.plugin import IPlugin, ScientificContract, ScientificReadinessLevel, PluginCapability

class IHeadModel(ABC):
    """
    Abstract interface for computing leadfield projections from cortical dipoles to surface electrodes.
    """
    @abstractmethod
    def compute_leadfield(self, dipole_positions: np.ndarray, electrode_positions: np.ndarray) -> np.ndarray:
        pass
    
    @property
    @abstractmethod
    def contract(self) -> ScientificContract:
        pass

class SphereModel(IHeadModel):
    """
    Tier 1 Head Model: Analytical spherical head model (always available, lightweight for CI).
    Assumes homogeneous spherical volume conductor.
    """
    def __init__(self, radius: float = 0.085, conductivity: float = 0.33):
        self.radius = radius
        self.conductivity = conductivity
        self.conductivity_uncertainty = IUncertainty(
            mean=conductivity,
            variance=0.01,
            distribution="normal",
            sample_size=1000,
            method="literature_variance"
        )
        
    @property
    def contract(self) -> ScientificContract:
        return ScientificContract(
            purpose="Compute leadfield for a single-sphere homogeneous head model",
            mathematical_assumptions=["Homogeneous spherical volume conductor", "Infinite homogeneous medium approximation for gradient"],
            numerical_assumptions=["Analytical solution avoids discretization error"],
            supported_modalities=[SignalType.EEG],
            unsupported_modalities=[SignalType.MEG, SignalType.ECOG, SignalType.SEEG],
            known_artifacts=["Spatial blurring"],
            expected_uncertainty=["High spatial error due to lack of skull anisotropy"],
            reference_implementations=["Standard EEG analytical models"],
            reference_software=["FieldTrip"],
            expected_numerical_tolerances={"potential": 1e-6},
            calibration_provenance="Literature conductivity values"
        )
        
    def compute_leadfield(self, dipole_positions: np.ndarray, electrode_positions: np.ndarray) -> np.ndarray:
        # TODO: Implement the correct single-sphere analytical solution (e.g., Frank 1952).
        # The previous implementation used an infinite homogeneous medium approximation 
        # (r_vec / (4 * pi * sigma * r_mag^3)), which is scientifically inaccurate for surface EEG.
        raise NotImplementedError("Single-sphere analytical solution is pending implementation.")

class BEMModel(IHeadModel):
    """
    Tier 2 Head Model: Boundary Element Method (MNE BEM). Requires external FreeSurfer dependencies.
    """
    def __init__(self, bem_file_path: str):
        self.bem_file_path = bem_file_path
        
    @property
    def contract(self) -> ScientificContract:
        return ScientificContract(
            purpose="Compute leadfield using Boundary Element Method",
            mathematical_assumptions=["Boundary Element Method (3-layer or 1-layer)"],
            supported_modalities=[SignalType.EEG, SignalType.MEG],
            unsupported_modalities=[SignalType.SEEG],
            numerical_assumptions=["Triangular mesh discretization"],
            known_artifacts=["Mesh boundary singularities"],
            expected_uncertainty=["Discretization error"],
            reference_implementations=["MNE-Python make_bem_model"],
            reference_software=["MNE", "FreeSurfer"],
            expected_numerical_tolerances={"bem_solution": 1e-4},
            calibration_provenance="MRI segmentation"
        )
        
    def compute_leadfield(self, dipole_positions: np.ndarray, electrode_positions: np.ndarray) -> np.ndarray:
        raise NotImplementedError("BEMModel requires MNE-Python and FreeSurfer dependencies. (Tier 2)")

class PatientSpecificModel(IHeadModel):
    """
    Tier 3 Head Model: High-resolution FEM from patient-specific MRI/CT.
    """
    def __init__(self, mesh_file_path: str):
        self.mesh_file_path = mesh_file_path
        
    @property
    def contract(self) -> ScientificContract:
        return ScientificContract(
            purpose="Compute leadfield using high-resolution Finite Element Method",
            mathematical_assumptions=["Finite Element Method (FEM)"],
            supported_modalities=[SignalType.EEG, SignalType.MEG, SignalType.SEEG, SignalType.ECOG],
            unsupported_modalities=[],
            numerical_assumptions=["Hexahedral or tetrahedral volume mesh"],
            known_artifacts=["Solver convergence issues"],
            expected_uncertainty=["Tissue conductivity assignment variance"],
            reference_implementations=["SimNIBS", "DUNEuro"],
            reference_software=["SimNIBS"],
            expected_numerical_tolerances={"fem_solution": 1e-5},
            calibration_provenance="Patient-specific MRI/CT"
        )
        
    def compute_leadfield(self, dipole_positions: np.ndarray, electrode_positions: np.ndarray) -> np.ndarray:
        raise NotImplementedError("PatientSpecificModel requires advanced FEM solvers. (Tier 3)")

class ForwardModel(IPlugin):
    """
    Maps cortical dipole activity through the leadfield to the surface electrodes,
    injecting spatial uncertainty (electrode displacement).
    """
    def __init__(self, head_model: IHeadModel, electrode_positions: np.ndarray, dipole_positions: np.ndarray):
        self.head_model = head_model
        self.electrode_positions = electrode_positions
        self.dipole_positions = dipole_positions
        self.displacement_uncertainty = IUncertainty(
            mean=0.0,
            variance=0.005, # 5mm displacement variance
            distribution="normal",
            sample_size=1,
            method="spatial_coregistration"
        )
        self._leadfield = None

    @property
    def plugin_id(self) -> str:
        return "vk:Model:ForwardProjection"

    @property
    def version(self) -> str:
        return "0.1.0"

    @property
    def srl(self) -> ScientificReadinessLevel:
        return ScientificReadinessLevel.SRL_2

    @property
    def contract(self) -> ScientificContract:
        base_contract = self.head_model.contract
        base_contract.mathematical_assumptions.append("Linear superposition of dipole fields (Y = L * X)")
        base_contract.purpose = "Project cortical source activity to sensor space"
        base_contract.known_artifacts.append("Inverse problem ill-posedness")
        base_contract.reference_implementations.append("MNE apply_forward")
        base_contract.reference_software.append("MNE")
        return base_contract

    @property
    def capabilities(self) -> List[PluginCapability]:
        return [PluginCapability(
            id="forward_modeling",
            version="0.1.0",
            consumes=["ISignal"],
            produces=["ISignal"],
            assumptions=["Quasi-static approximation of Maxwell's equations"],
            uncertainty_model=["Electrode displacement variance"]
        )]

    @property
    def inputs(self) -> List[Type[IScientificObject]]:
        return [ISignal] # Dipole moments as ISignal

    @property
    def outputs(self) -> List[Type[IScientificObject]]:
        return [ISignal] # Sensor data as ISignal

    def execute(self, inputs: Dict[str, IScientificObject]) -> Dict[str, IScientificObject]:
        """
        Projects source activity to sensor space.
        Expects 'dipole_moments' in inputs.
        dipole_moments.data should be (N_dipoles * 3, N_times)
        """
        dipole_signal = inputs.get("dipole_moments")
        if not isinstance(dipole_signal, ISignal):
            raise ValueError("Expected ISignal as 'dipole_moments' input")
            
        if self._leadfield is None:
            self._leadfield = self.head_model.compute_leadfield(self.dipole_positions, self.electrode_positions)
            
        dipole_moments = dipole_signal.data
        # Y = L * X
        sensor_data = self._leadfield @ dipole_moments
        
        return {"sensor_data": ISignal(sampling_rate=dipole_signal.sampling_rate, data=sensor_data)}
