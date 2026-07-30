# Copyright 2026 VIREON Contributors
# Zero-Trust Enforcement Proxies

from typing import Any
from vireon.sdk.services.apis import IStateAPI, ITelemetryAPI
from vireon.sdk.capability.descriptor import CapabilityDescriptor

class SecurityFault(Exception):
    """Raised when a provider attempts an action outside its capability descriptor."""
    pass

class EnforcingStateAPI(IStateAPI):
    """
    Wraps the global State Store. Blocks unauthorized reads or mutations 
    based on the provider's capability descriptor.
    """
    def __init__(self, global_store: Any, descriptor: CapabilityDescriptor):
        self._global_store = global_store
        self._descriptor = descriptor
        
        # Parse permissions exactly to prevent bypass via substring matching
        self._can_read_all = 'state.read:*' in descriptor.permissions
        self._can_mutate_all = 'state.mutate:*' in descriptor.permissions

    def get(self, key: str, default: Any = None) -> Any:
        if not self._can_read_all and f'state.read:{key}' not in self._descriptor.permissions:
            raise SecurityFault(f"Provider '{self._descriptor.id}' lacks 'state.read' capability for key: {key}")
        
        # Handle fallback for older dictionary-based state stores during migration
        if isinstance(self._global_store, dict):
            return self._global_store.get(key, default)
        
        # If it's a newer store that handles default, pass it. If not, fallback.
        try:
            return self._global_store.get(key, default)
        except TypeError:
            val = self._global_store.get(key)
            return val if val is not None else default

    def set(self, key: str, value: Any) -> None:
        if not self._can_mutate_all and f'state.mutate:{key}' not in self._descriptor.permissions:
            raise SecurityFault(f"Provider '{self._descriptor.id}' lacks 'state.mutate' capability for key: {key}")
            
        if isinstance(self._global_store, dict):
            self._global_store[key] = value
        else:
            self._global_store.set(key, value, source=self._descriptor.id)

class EnforcingTelemetryAPI(ITelemetryAPI):
    """
    Wraps the global Event Bus for telemetry.
    """
    def __init__(self, global_bus: Any, descriptor: CapabilityDescriptor):
        self._global_bus = global_bus
        self._descriptor = descriptor
        self._can_publish = 'event.publish' in descriptor.permissions or 'event.publish:telemetry' in descriptor.permissions

    def publish(self, channel: int, value: float) -> None:
        if not self._can_publish:
            raise SecurityFault(f"Provider '{self._descriptor.id}' lacks 'event.publish' capability.")
            
        if hasattr(self._global_bus, "publish"):
            from vireon.sdk.schemas.events import TelemetryEvent
            event = TelemetryEvent(
                topic="telemetry",
                source_id=self._descriptor.id,
                timestamp=0.0, # Filled by orchestrator or clock
                channel=channel,
                value=value
            )
            self._global_bus.publish(event)
