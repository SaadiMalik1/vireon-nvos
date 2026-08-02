import pytest
import os
import importlib.metadata
from importlib.metadata import EntryPoint
from typing import Dict, Any, List, Type

from vireon_core.kernel.plugins import PluginManager, PluginLoadResult
from vireon_core.contracts.plugin import IPlugin, ScientificContract, ScientificReadinessLevel, PluginCapability

class TestPlugin(IPlugin):
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
    def inputs(self) -> List[Type]:
        return []
        
    @property
    def outputs(self) -> List[Type]:
        return []
        
    @property
    def plugin_type(self) -> str:
        return "test"
        
    def initialize(self, config: Dict[str, Any]) -> None:
        pass
        
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        return inputs


class SomeTestPlugin(IPlugin):
    @property
    def plugin_id(self) -> str: return "test.some_plugin"
    @property
    def version(self) -> str: return "1.0.0"
    @property
    def srl(self) -> ScientificReadinessLevel: return ScientificReadinessLevel.SRL_0
    @property
    def contract(self) -> ScientificContract: return ScientificContract()
    @property
    def capabilities(self) -> List[PluginCapability]: return []
    @property
    def inputs(self) -> List[Type]: return []
    @property
    def outputs(self) -> List[Type]: return []
    @property
    def plugin_type(self) -> str: return "test"
    def initialize(self, config: Dict[str, Any]) -> None: pass
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]: return inputs


def test_entry_point_discovery_finds_registered_plugin(monkeypatch):
    """A plugin registered via entry_points in pyproject.toml is discoverable."""
    mock_ep = EntryPoint(name="test_plugin", value=f"{__name__}:TestPlugin", group="vireon.plugins")
    real_eps = list(importlib.metadata.entry_points(group="vireon.plugins"))
    if not any(ep.name == "test_plugin" for ep in real_eps):
        monkeypatch.setattr(
            importlib.metadata,
            "entry_points",
            lambda group=None: [mock_ep] if group == "vireon.plugins" else {"vireon.plugins": [mock_ep]}
        )

    pm = PluginManager()
    results = pm.discover()
    assert isinstance(results, list)
    plugin_ids = [r.plugin_id for r in results if r.success]
    assert "test.discovery.plugin" in plugin_ids, f"TestPlugin not discovered. Found: {plugin_ids}"
    
    discovered_plugin = pm.get_plugin("test.discovery.plugin")
    assert discovered_plugin is not None
    assert isinstance(discovered_plugin, IPlugin)
    assert discovered_plugin.plugin_id == "test.discovery.plugin"


def test_filesystem_discovery_finds_py_files(tmp_path):
    """A .py file in the scan directory is imported and its plugins registered."""
    plugin_file = tmp_path / "my_plugin.py"
    plugin_file.write_text("""
from typing import Dict, Any, List, Type
from vireon_core.contracts.plugin import IPlugin, ScientificContract, ScientificReadinessLevel, PluginCapability

class MyPlugin(IPlugin):
    @property
    def plugin_id(self) -> str: return "test.my_plugin"
    @property
    def version(self) -> str: return "1.0.0"
    @property
    def srl(self) -> ScientificReadinessLevel: return ScientificReadinessLevel.SRL_0
    @property
    def contract(self) -> ScientificContract: 
        c = ScientificContract()
        if hasattr(c, "capabilities_provided"):
            c.capabilities_provided = ["spectral_analysis"]
        return c
    @property
    def capabilities(self) -> List[PluginCapability]: return []
    @property
    def inputs(self) -> List[Type]: return []
    @property
    def outputs(self) -> List[Type]: return []
    @property
    def plugin_type(self) -> str: return "test"
    def initialize(self, config: Dict[str, Any]) -> None: pass
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]: return inputs
""")
    pm = PluginManager(scan_dir=str(tmp_path))
    pm.discover()
    assert pm.get_plugin("test.my_plugin") is not None


def test_capability_routing_returns_only_matching_plugins():
    """get_plugin_by_capability filters by declared capabilities."""
    pm = PluginManager()
    
    class SpectralPlugin(SomeTestPlugin):
        @property
        def plugin_id(self) -> str: return "test.spectral"
        @property
        def contract(self) -> ScientificContract: 
            c = ScientificContract()
            if hasattr(c, "capabilities_provided"):
                c.capabilities_provided = ["spectral_analysis"]
            return c

    plugin2 = SpectralPlugin()
    pm.register_plugin(plugin2, config={})
    
    spectral_plugins = pm.get_plugin_by_capability("spectral_analysis")
    assert len(spectral_plugins) == 1
    assert spectral_plugins[0].plugin_id == "test.spectral"
    
    other_plugins = pm.get_plugin_by_capability("source_localization")
    assert len(other_plugins) == 0


def test_failing_plugin_does_not_crash_manager(tmp_path):
    """A plugin that raises in initialize() is marked failed, not crashing."""
    plugin_file = tmp_path / "failing_plugin.py"
    plugin_file.write_text("""
from typing import Dict, Any, List, Type
from vireon_core.contracts.plugin import IPlugin, ScientificContract, ScientificReadinessLevel, PluginCapability

class FailingPlugin(IPlugin):
    @property
    def plugin_id(self) -> str: return "test.failing"
    @property
    def version(self) -> str: return "1.0.0"
    @property
    def srl(self) -> ScientificReadinessLevel: return ScientificReadinessLevel.SRL_0
    @property
    def contract(self) -> ScientificContract: return ScientificContract()
    @property
    def capabilities(self) -> List[PluginCapability]: return []
    @property
    def inputs(self) -> List[Type]: return []
    @property
    def outputs(self) -> List[Type]: return []
    @property
    def plugin_type(self) -> str: return "test"
    def initialize(self, config: Dict[str, Any]) -> None: raise ValueError("Fail")
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]: return inputs
""")
    pm = PluginManager(scan_dir=str(tmp_path))
    results = pm.discover()
    
    failing_result = next((r for r in results if r.plugin_id == "test.failing" and not r.success), None)
    assert failing_result is not None
    assert "Fail" in str(failing_result.error)
    assert pm.get_plugin("test.failing") is None


def test_backward_compat_register_and_get():
    """The old register_plugin/get_plugin API still works."""
    pm = PluginManager()
    plugin = SomeTestPlugin()
    pm.register_plugin(plugin, config={})
    assert pm.get_plugin(plugin.plugin_id) is plugin
