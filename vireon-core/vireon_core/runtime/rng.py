# Copyright 2026 VIREON Contributors
# SPDX-License-Identifier: MIT


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

    def permutation(self, x: Any) -> Any:
        return self._generator.permutation(x)

    def choice(self, a: Any, size: Optional[Any] = None, replace: bool = True, p: Optional[Any] = None) -> Any:
        return self._generator.choice(a, size=size, replace=replace, p=p)

    def beta(self, a: float, b: float, size: Optional[Tuple[int, ...]] = None) -> Any:
        return self._generator.beta(a, b, size)

    def get_state(self) -> dict:
        return {
            "initial_seed": self.initial_seed,
            "bit_generator": self._generator.bit_generator.state,
        }
