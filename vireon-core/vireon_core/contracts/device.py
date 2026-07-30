from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class IHardwareDevice(ABC):
    """
    Base abstraction for a neurotechnology device.
    """
    @abstractmethod
    def get_hardware_specs(self) -> Dict[str, Any]:
        pass

class ReferenceDevice(IHardwareDevice):
    """
    A reference hardware platform (e.g., ADS1299, Intan RHD).
    Used as ground-truth baselines for benchmarking.
    """
    def __init__(self, name: str, specs: Dict[str, Any]):
        self.name = name
        self.specs = specs

    def get_hardware_specs(self) -> Dict[str, Any]:
        return self.specs

class CommercialDevice(IHardwareDevice):
    """
    A specific commercial medical device (e.g., Neuralink, Medtronic Percept).
    """
    def __init__(self, name: str, manufacturer: str, specs: Dict[str, Any]):
        self.name = name
        self.manufacturer = manufacturer
        self.specs = specs

    def get_hardware_specs(self) -> Dict[str, Any]:
        return self.specs

class VirtualDevice(IHardwareDevice):
    """
    A user-defined software-emulated hardware model for stress-testing.
    """
    def __init__(self, name: str, specs: Dict[str, Any]):
        self.name = name
        self.specs = specs

    def get_hardware_specs(self) -> Dict[str, Any]:
        return self.specs
