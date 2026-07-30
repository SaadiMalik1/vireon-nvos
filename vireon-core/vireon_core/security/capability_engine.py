# Copyright 2026 VIREON Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Any
from vireon.sdk.manifest import CapabilityManifest
from vireon_core.runtime.configuration import ExperimentConfig

class CapabilityViolationError(Exception):
    pass

class CapabilityEngine:
    def __init__(self, config: ExperimentConfig):
        self.config = config

    def validate_manifest(self, manifest: CapabilityManifest, trusted_public_key=None) -> bool:
        """
        Validates whether requested capabilities are allowed by ExperimentConfig,
        and optionally verifies cryptographic Ed25519 vendor signature.
        """
        if not self.config.security.enabled:
            return True

        if self.config.security.enable_zta:
            if manifest.requires_host_access:
                return False

        if trusted_public_key:
            if not manifest.signature_bytes or not manifest.verify_signature(trusted_public_key):
                return False

        return True


class EventBusProxy:
    """Wraps an EventBus, enforcing a provider's pub/sub capabilities."""
    def __init__(self, real_bus, manifest: CapabilityManifest):
        self._bus = real_bus
        self._manifest = manifest

    def publish(self, event) -> None:
        if event.topic not in self._manifest.publishes_events and "*" not in self._manifest.publishes_events:
            raise CapabilityViolationError(f"Provider {self._manifest.name} not authorized to publish to {event.topic}")
        self._bus.publish(event)

    def subscribe(self, topic, handler, priority=100) -> str:
        if topic not in self._manifest.subscribes_events and "*" not in self._manifest.subscribes_events:
            raise CapabilityViolationError(f"Provider {self._manifest.name} not authorized to subscribe to {topic}")
        return self._bus.subscribe(topic, handler, priority)

class StateStoreProxy:
    """Wraps a StateStore, enforcing a provider's read/mutate capabilities."""
    def __init__(self, real_store, manifest: CapabilityManifest):
        self._store = real_store
        self._manifest = manifest

    def get(self, key: str, default: Any = None) -> Any:
        if key not in self._manifest.reads_state and "*" not in self._manifest.reads_state:
            raise CapabilityViolationError(f"Provider {self._manifest.name} not authorized to read state {key}")
        return self._store.get(key, default)

    def set(self, key: str, value: Any) -> None:
        if key not in self._manifest.mutates_state and "*" not in self._manifest.mutates_state:
            raise CapabilityViolationError(f"Provider {self._manifest.name} not authorized to mutate state {key}")
        self._store.set(key, value, source=self._manifest.name)
