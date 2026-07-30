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
Deterministic Clock & Bifurcated Scheduler Implementation (ADR-004, ADR-005).

Provides virtual step-time advancement for reproducible simulation replay,
high-precision monotonic wall-clock synchronization, and event scheduling.
"""

from enum import Enum
import time
import threading
from typing import Callable, List, Tuple, Optional


class ClockMode(str, Enum):
    VIRTUAL = "VIRTUAL"
    WALL = "WALL"


class DeterministicClock:
    """
    Deterministic Clock (ADR-004, ADR-005).
    Controls discrete virtual time ticks and time-delta advancement.
    """

    def __init__(self, mode: ClockMode = ClockMode.VIRTUAL, initial_time: float = 0.0, step_dt_ms: float = 4.0):
        self._lock = threading.RLock()
        self.mode = mode
        self._initial_time = initial_time
        self.sim_time = initial_time
        self.tick_count = 0
        self.step_dt_ms = step_dt_ms
        self.step_dt_sec = step_dt_ms / 1000.0
        self._wall_start_time = time.monotonic()

    def advance(self, dt_sec: Optional[float] = None) -> float:
        with self._lock:
            if self.mode == ClockMode.VIRTUAL:
                self.tick_count += 1
                if dt_sec is None:
                    self.sim_time = self._initial_time + (self.tick_count * self.step_dt_sec)
                else:
                    self.sim_time += dt_sec
            else:
                current_wall = time.monotonic()
                self.sim_time = current_wall - self._wall_start_time
                self.tick_count += 1

            return self.sim_time

    def set_time(self, new_time: float) -> None:
        with self._lock:
            self.sim_time = new_time
            self._initial_time = new_time
            self.tick_count = 0

    def reset(self) -> None:
        with self._lock:
            self.sim_time = 0.0
            self._initial_time = 0.0
            self.tick_count = 0
            self._wall_start_time = time.monotonic()

    def get_state(self) -> dict:
        with self._lock:
            return {
                "mode": self.mode.value,
                "sim_time": self.sim_time,
                "tick_count": self.tick_count,
                "step_dt_ms": self.step_dt_ms,
            }


class BifurcatedScheduler:
    """
    Bifurcated Clock Scheduler (ADR-005).
    Schedules and dispatches periodic callbacks aligned with the DeterministicClock.
    """

    def __init__(self, clock: Optional[DeterministicClock] = None):
        self.clock = clock or DeterministicClock()
        self._scheduled_tasks: List[Tuple[float, Callable[[], None]]] = []
        self._lock = threading.RLock()

    def schedule(self, delay_sec: float, callback: Callable[[], None]) -> float:
        with self._lock:
            target_time = self.clock.sim_time + delay_sec
            self._scheduled_tasks.append((target_time, callback))
            self._scheduled_tasks.sort(key=lambda item: item[0])
            return target_time

    def tick_and_dispatch(self, dt_sec: Optional[float] = None) -> List[Callable[[], None]]:
        with self._lock:
            current_time = self.clock.advance(dt_sec)
            executed_callbacks = []
            remaining_tasks = []

            for target_time, callback in self._scheduled_tasks:
                if current_time >= target_time:
                    try:
                        callback()
                        executed_callbacks.append(callback)
                    except Exception as e:
                        # Fail-safe execution containment
                        print(f"[BifurcatedScheduler] Task execution error: {e}")
                else:
                    remaining_tasks.append((target_time, callback))

            self._scheduled_tasks = remaining_tasks
            return executed_callbacks
