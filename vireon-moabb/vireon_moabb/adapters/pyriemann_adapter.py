from vireon_moabb.adapters.base import BaseAdapter, AdapterResult

class PyriemannAdapter(BaseAdapter):
    @property
    def name(self) -> str: return "pyriemann"
    
    @property
    def library_version(self) -> str: return "unknown"
    
    def can_handle(self, spec: dict) -> bool: return spec.get("library") == "pyriemann"
    
    def execute(self, spec: dict, **kwargs) -> AdapterResult:
        return AdapterResult(outputs=None, metadata={}, execution_hash="mock", adapter_name=self.name)
