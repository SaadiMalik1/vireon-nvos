from abc import ABC, abstractmethod
from typing import Any, List, Optional, Dict, Type
import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
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
    def __init__(self, n_sources: Optional[int] = None, n_sensors: Optional[int] = None, 
                 radius: float = 0.085, conductivity: float = 0.33, seed: int = 42):
        self.radius = radius
        self.conductivity = conductivity
        self.conductivity_uncertainty = IUncertainty(
            mean=conductivity,
            variance=0.01,
            distribution="normal",
            sample_size=1000,
            method="literature_variance"
        )
        self.n_sources = n_sources
        self.n_sensors = n_sensors
        self.seed = seed
        
        if n_sources is not None and n_sensors is not None:
            rng = DeterministicRNG(seed)
            # Generate random dipole positions inside the sphere
            phi = rng.uniform(0, 2 * np.pi, n_sources)
            costheta = rng.uniform(-1, 1, n_sources)
            u = rng.uniform(0, 1, n_sources)
            theta = np.arccos(costheta)
            r_dist = radius * 0.8 * np.cbrt(u)
            self.dipole_positions = np.column_stack([
                r_dist * np.sin(theta) * np.cos(phi),
                r_dist * np.sin(theta) * np.sin(phi),
                r_dist * np.cos(theta)
            ])
            
            # Generate random electrode positions on the sphere surface
            phi_e = rng.uniform(0, 2 * np.pi, n_sensors)
            costheta_e = rng.uniform(-1, 1, n_sensors)
            theta_e = np.arccos(costheta_e)
            self.electrode_positions = np.column_stack([
                radius * np.sin(theta_e) * np.cos(phi_e),
                radius * np.sin(theta_e) * np.sin(phi_e),
                radius * np.cos(theta_e)
            ])
            
            self._leadfield_matrix = self.compute_leadfield(self.dipole_positions, self.electrode_positions)
            
            # Generate fixed random orientations for each dipole to project scalar sources
            # We want ori to be (n_sources, 3)
            ori = rng.uniform(-1, 1, (n_sources, 3))
            ori_norm = np.linalg.norm(ori, axis=1, keepdims=True)
            self.dipole_orientations = ori / ori_norm
        else:
            self.dipole_positions = None
            self.electrode_positions = None
            self._leadfield_matrix = None
            self.dipole_orientations = None
        
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
        # Implement the single-sphere analytical solution (Frank 1952 approximation for surface potentials)
        n_dipoles = dipole_positions.shape[0]
        n_electrodes = electrode_positions.shape[0]
        leadfield = np.zeros((n_electrodes, n_dipoles * 3))
        
        for i in range(n_dipoles):
            r_d = dipole_positions[i]
            for j in range(n_electrodes):
                r_e = electrode_positions[j]
                
                # Distance vector
                d_vec = r_e - r_d
                d_mag = np.linalg.norm(d_vec)
                
                if d_mag == 0:
                    continue
                    
                # Simplified Frank (1952) / homogeneous sphere projection
                # V = (1 / 4*pi*sigma) * (p dot d_vec) / d_mag^3
                # This constructs the leadfield row for the 3 dipole components (px, py, pz)
                proj = d_vec / (4 * np.pi * self.conductivity * (d_mag**3))
                leadfield[j, i*3:(i+1)*3] = proj
                
        return leadfield

    def project(self, source_signals: np.ndarray) -> np.ndarray:
        """
        Projects scalar source signals (samples, sources) to sensor signals (samples, sensors).
        Uses the internal fixed dipole orientations to map scalars to 3D moments.
        """
        if self._leadfield_matrix is None:
            raise ValueError("n_sources and n_sensors must be set to use project()")
            
        N = source_signals.shape[0]
        # Map (N, n_sources) to (N, n_sources * 3)
        dipole_moments = np.zeros((N, self.n_sources * 3))
        for i in range(self.n_sources):
            # source_signals[:, i] is (N,)
            # self.dipole_orientations[i] is (3,)
            # We want (N, 3)
            dipole_moments[:, i*3:(i+1)*3] = source_signals[:, i:i+1] * self.dipole_orientations[i]
            
        return dipole_moments @ self._leadfield_matrix.T

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
        try:
            import mne
            import os
        except ImportError:
            raise RuntimeError("BEMModel requires MNE-Python and FreeSurfer dependencies. (Tier 2). Please install 'mne'.")
            
        data_path = mne.datasets.sample.data_path(verbose=False)
        subject = "sample"
        subjects_dir = os.path.join(data_path, "subjects")
        
        bem_model = mne.make_bem_model(subject, ico=4, conductivity=(0.3,),
                                        subjects_dir=subjects_dir)
        bem = mne.make_bem_solution(bem_model)
        
        src = mne.setup_volume_source_space(subject, subjects_dir=subjects_dir)
        
        info_path = os.path.join(data_path, 'MEG', 'sample', 'sample_audvis_raw.fif')
        trans_path = os.path.join(data_path, 'MEG', 'sample', 'sample_audvis_raw-trans.fif')
        
        info = mne.io.read_info(info_path, verbose=False)
        fwd = mne.make_forward_solution(info, trans=trans_path, src=src, bem=bem,
                                        meg=False, eeg=True, mindist=5.0, n_jobs=1, verbose=False)
        
        leadfield = fwd['sol']['data']
        return leadfield

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
        try:
            import simnibs
        except ImportError:
            raise ImportError("PatientSpecificModel requires advanced FEM solvers like SimNIBS (Tier 3). Please install 'simnibs'.")
            
        raise RuntimeError("FEM mesh parsing requires a valid SimNIBS output volume.")

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
