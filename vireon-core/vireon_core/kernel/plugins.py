from typing import Dict, Any, Type, Optional
from vireon_core.contracts.plugin import IPlugin

class PluginManager:
    """
    Manages discovery, registration, and lifecycle of VIREON plugins.
    """
    def __init__(self):
        self._plugins: Dict[str, IPlugin] = {}
        
    def register_plugin(self, plugin: IPlugin, config: Optional[Dict[str, Any]] = None):
        """Registers and initializes a plugin."""
        if not config:
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
