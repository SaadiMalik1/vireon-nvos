import os
import sys
import importlib.metadata
import importlib.util
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from vireon_core.contracts.plugin import (
    IPlugin,
    ScientificContract,
    ScientificReadinessLevel,
    PluginCapability,
)

logger = logging.getLogger(__name__)

class PluginLoadResult(BaseModel):
    plugin_id: str
    success: bool
    error: Optional[str] = None


class SampleDiscoveryPlugin(IPlugin):
    @property
    def plugin_id(self) -> str:
        return "test.discovery.plugin"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def srl(self) -> ScientificReadinessLevel:
        return ScientificReadinessLevel.SRL_0

    @property
    def contract(self) -> ScientificContract:
        return ScientificContract()

    @property
    def capabilities(self) -> List[PluginCapability]:
        return []

    @property
    def inputs(self) -> List[type]:
        return []

    @property
    def outputs(self) -> List[type]:
        return []

    @property
    def plugin_type(self) -> str:
        return "test"

    def initialize(self, config: Dict[str, Any]) -> None:
        pass

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        return inputs

class PluginManager:
    """
    Manages discovery, registration, and lifecycle of VIREON plugins.
    """
    def __init__(self, scan_dir: Optional[str] = None):
        self._plugins: Dict[str, IPlugin] = {}
        if scan_dir is None:
            self.scan_dir = os.environ.get("VIREON_PLUGIN_DIR", os.path.expanduser("~/.vireon/plugins/"))
        else:
            self.scan_dir = scan_dir
            
    def register_plugin(self, plugin: IPlugin, config: Optional[Dict[str, Any]] = None):
        """Registers and initializes a plugin."""
        if config is None:
            config = {}
        plugin.initialize(config)
        self._plugins[plugin.plugin_id] = plugin
        
    def get_plugin(self, plugin_id: str) -> Optional[IPlugin]:
        return self._plugins.get(plugin_id)
        
    def get_plugins_by_type(self, plugin_type: str) -> Dict[str, IPlugin]:
        """Returns all registered plugins of a specific type."""
        return {
            pid: p for pid, p in self._plugins.items() if p.plugin_type == plugin_type
        }
        
    def get_plugin_by_capability(self, capability: str) -> List[IPlugin]:
        """Filters plugins by their ScientificContract.capabilities_provided field."""
        result = []
        for p in self._plugins.values():
            if hasattr(p.contract, "capabilities_provided") and capability in p.contract.capabilities_provided:
                result.append(p)
        return result

    def _safe_initialize(self, plugin: IPlugin, config: Dict[str, Any]) -> PluginLoadResult:
        try:
            self.register_plugin(plugin, config)
            return PluginLoadResult(plugin_id=plugin.plugin_id, success=True)
        except Exception as e:
            logger.error(f"Failed to initialize plugin {plugin.plugin_id}: {e}")
            return PluginLoadResult(plugin_id=plugin.plugin_id, success=False, error=str(e))

    def discover(self, config: Optional[Dict[str, Any]] = None) -> List[PluginLoadResult]:
        if config is None:
            config = {}
        results = []
        
        # 1. Entry points discovery
        try:
            # For python >= 3.10
            entry_points = importlib.metadata.entry_points(group="vireon.plugins")
        except TypeError:
            # For python < 3.10
            eps = importlib.metadata.entry_points()
            entry_points = eps.get("vireon.plugins", [])
            
        for ep in entry_points:
            try:
                plugin_cls = ep.load()
                plugin_instance = plugin_cls()
                results.append(self._safe_initialize(plugin_instance, config))
            except Exception as e:
                logger.error(f"Failed to load entry point {ep.name}: {e}")
                results.append(PluginLoadResult(plugin_id=ep.name, success=False, error=str(e)))
                
        # 2. Filesystem scan
        if os.path.exists(self.scan_dir) and os.path.isdir(self.scan_dir):
            for filename in os.listdir(self.scan_dir):
                if filename.endswith(".py") and not filename.startswith("__"):
                    filepath = os.path.join(self.scan_dir, filename)
                    module_name = f"vireon_plugin_fs_{filename[:-3]}"
                    try:
                        spec = importlib.util.spec_from_file_location(module_name, filepath)
                        if spec and spec.loader:
                            module = importlib.util.module_from_spec(spec)
                            sys.modules[module_name] = module
                            spec.loader.exec_module(module)
                            
                            for attr_name in dir(module):
                                attr = getattr(module, attr_name)
                                if isinstance(attr, type) and issubclass(attr, IPlugin) and attr is not IPlugin:
                                    plugin_instance = attr()
                                    results.append(self._safe_initialize(plugin_instance, config))
                    except Exception as e:
                        logger.error(f"Failed to load filesystem plugin {filename}: {e}")
                        results.append(PluginLoadResult(plugin_id=filename, success=False, error=str(e)))
                        
        return results
        
    def initialize(self, config: Dict[str, Any]) -> None:
        """Lifecycle hook: initialize manager."""
        pass

    def start(self):
        """Lifecycle hook: start all plugins."""
        pass
        
    def stop(self):
        """Lifecycle hook: stop all plugins."""
        pass
        
    def health_check(self) -> Dict[str, Any]:
        """Lifecycle hook: check health of all plugins."""
        return {"status": "ok", "plugins": len(self._plugins)}
