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

"""
Deterministic RNG Implementation (ADR-004).

Provides seed-managed pseudo-random number generation wrapper ensuring reproducible
noise generation and simulation stream outputs across re-runs.
"""

from typing import Optional, Tuple, Any

import numpy as np


class DeterministicRNG:
    """
    Owned Deterministic Pseudo-Random Number Generator (ADR-004).
    Enforces seed reproducibility across digital twin signal & noise models.
    """

    def __init__(self, seed: Optional[int] = 42):
        self.initial_seed = seed
        self._generator = np.random.default_rng(seed)

    def reseed(self, seed: Optional[int] = None) -> None:
        if seed is not None:
            self.initial_seed = seed
        self._generator = np.random.default_rng(self.initial_seed)

    def normal(self, loc: float = 0.0, scale: float = 1.0, size: Optional[Tuple[int, ...]] = None) -> Any:
        return self._generator.normal(loc, scale, size)

    def uniform(self, low: float = 0.0, high: float = 1.0, size: Optional[Tuple[int, ...]] = None) -> Any:
        return self._generator.uniform(low, high, size)

    def integer(self, low: int, high: int, size: Optional[Tuple[int, ...]] = None) -> Any:
        return self._generator.integers(low, high, size)


    def get_state(self) -> dict:
        return {
            "initial_seed": self.initial_seed,
            "bit_generator": type(self._generator.bit_generator).__name__,
        }
