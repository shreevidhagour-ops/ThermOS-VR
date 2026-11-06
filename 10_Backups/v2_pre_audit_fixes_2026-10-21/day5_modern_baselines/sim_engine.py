"""
Unified discrete-time simulation engine for ThermOS-VR v2 experiments.

Every scheduling policy runs inside the same time loop, with the same
thermal model, DVFS governor, logging rule and metric definitions.
The original day1/day2 Process, Core and ThermalModel classes are reused
unchanged.

One simulation tick = one time unit, as in v1. Tick order:

    1. Dispatch     policy.schedule(t, ready, cores) returns the task for
                    every core during [t, t+1)
    2. Execute      each busy core performs frequency / 2.5 work units
    3. Thermal      core temperature is updated using the frequency that
                    was in effect during the tick
    4. DVFS         governor may change frequency for the next tick
    5. Advance      t = t + 1
    6. Complete     tasks with no remaining work finish at time t
    7. Log          one row per core describing the tick [t-1, t)
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))

for _folder in ("day1_basic_scheduler", "day2_thermal_model"):
    _path = os.path.abspath(os.path.join(_HERE, "..", _folder))
    if _path not in sys.path:
        sys.path.append(_path)

from core import Core  # noqa: E402
from thermal_model import ThermalModel  # noqa: E402


REFERENCE_FREQUENCY = 2.5
EPSILON = 1e-9

# Same thermal parameters as v1 (day4_experiments/simulation_engine.py).
DEFAULT_THERMAL_PARAMETERS = {
    "ambient_temperature": 25.0,
    "initial_temperature": 45.0,
    "heat_coefficient": 1.0,
    "cooling_coefficient": 0.02,
    "reference_frequency": REFERENCE_FREQUENCY,
}


def create_cores(thermal_parameters=None):
    """
    Create the same two-core platform used in v1.

    Note: "Performance" and "Efficiency" are labels only. Both cores
    share identical frequency levels, speed and thermal parameters.
    """

    parameters = dict(DEFAULT_THERMAL_PARAMETERS)
    parameters.update(thermal_parameters or {})

    cores = [
        Core(core_id=1, core_type="Performance"),
        Core(core_id=2, core_type="Efficiency"),
    ]

    for core in cores:
        core.temperature = parameters["initial_temperature"]
        core.frequency = REFERENCE_FREQUENCY
        core.thermal_model = ThermalModel(**parameters)

    return cores


# ============================================================
# DVFS GOVERNORS
# ============================================================

class NoDVFSGovernor:
    """Fixed 2.5 GHz. No thermal management."""

    name = "off"

    def update(self, core):
        pass


class LegacyHysteresisGovernor:
    """
    Exact copy of the v1 update_frequency() logic, including bug B2
    (no downward transition below 2.2 GHz). Used only by the legacy
    equivalence tests.
    """

    name = "legacy"

    def update(self, core):
        temperature = core.temperature

        if core.frequency == 2.5:
            if temperature >= 60:
                core.frequency = 2.2
        elif core.frequency == 2.2:
            if temperature <= 58:
                core.frequency = 2.5
        elif core.frequency == 1.8:
            if temperature <= 68:
                core.frequency = 2.2
        elif core.frequency == 1.4:
            if temperature <= 78:
                core.frequency = 1.8


class HysteresisDVFSGovernor:
    """
    Corrected four-level thermal DVFS governor with hysteresis.

    Step down one level when temperature reaches the threshold of the
    next thermal state; step up one level only after cooling 2 °C below
    that threshold. At most one step per tick (same as v1).

        2.5 GHz -> 2.2 GHz at >= 60 °C   (COOL -> WARM)
        2.2 GHz -> 1.8 GHz at >= 70 °C   (WARM -> HOT)
        1.8 GHz -> 1.4 GHz at >= 80 °C   (HOT  -> CRITICAL)

        1.4 GHz -> 1.8 GHz at <= 78 °C
        1.8 GHz -> 2.2 GHz at <= 68 °C
        2.2 GHz -> 2.5 GHz at <= 58 °C
    """

    name = "hysteresis"

    LEVELS = (2.5, 2.2, 1.8, 1.4)
    STEP_DOWN_AT = {2.5: 60.0, 2.2: 70.0, 1.8: 80.0}
    STEP_UP_AT = {2.2: 58.0, 1.8: 68.0, 1.4: 78.0}

    def update(self, core):
        frequency = core.frequency
        index = self.LEVELS.index(frequency)

        if (
            frequency in self.STEP_DOWN_AT
            and core.temperature >= self.STEP_DOWN_AT[frequency]
        ):
            core.frequency = self.LEVELS[index + 1]

        elif (
            frequency in self.STEP_UP_AT
            and core.temperature <= self.STEP_UP_AT[frequency]
        ):
            core.frequency = self.LEVELS[index - 1]


GOVERNORS = {
    "off": NoDVFSGovernor,
    "hysteresis": HysteresisDVFSGovernor,
    "legacy": LegacyHysteresisGovernor,
}


# ============================================================
# SIMULATOR
# ============================================================

class SchedulingError(RuntimeError):
    pass


class Simulator:

    def __init__(self, processes, cores, policy, governor, max_time=10000):
        self.processes = processes
        self.cores = cores
        self.policy = policy
        self.governor = governor
        self.max_time = max_time
        self.trace = []

    @staticmethod
    def is_done(process):
        return process.completion_time is not None

    def _reset_processes(self):
        for process in self.processes:
            process.start_time = None
            process.completion_time = None
            process.waiting_time = 0
            process.turnaround_time = 0
            process.remaining_time = process.burst_time
            process.executed_work = 0.0
            process.deadline_missed = False

            process.response_time = None
            process.preemptions = 0
            process.migrations = 0
            process.last_core_id = None
            process.busy_ticks = 0

    def _validate(self, mapping, t):
        if set(mapping) != {core.core_id for core in self.cores}:
            raise SchedulingError(f"t={t}: mapping must cover every core")

        assigned = [task for task in mapping.values() if task is not None]

        if len({id(task) for task in assigned}) != len(assigned):
            raise SchedulingError(f"t={t}: a task was assigned to two cores")

        for task in assigned:
            if task.arrival_time > t or self.is_done(task):
                raise SchedulingError(
                    f"t={t}: {task.name} is not runnable"
                )

    def _apply(self, mapping, t):
        cores_by_id = {core.core_id: core for core in self.cores}
        newly_assigned = {id(task) for task in mapping.values() if task}

        # Release first so that a task may move between cores.
        for core in self.cores:
            old = core.current_process
            new = mapping[core.core_id]

            if old is not None and old is not new:
                if id(old) not in newly_assigned:
                    old.preemptions += 1
                core.release_process()

        for core_id, task in mapping.items():
            core = cores_by_id[core_id]

            if task is None or core.current_process is task:
                continue

            if task.start_time is None:
                task.start_time = t
                task.response_time = t - task.arrival_time

            if (
                task.last_core_id is not None
                and task.last_core_id != core_id
            ):
                task.migrations += 1

            core.assign_process(task)
            task.last_core_id = core_id

    def run(self):
        self._reset_processes()

        if hasattr(self.policy, "reset"):
            self.policy.reset(self.processes, self.cores)

        self.trace = []
        t = 0

        while not all(self.is_done(p) for p in self.processes):

            if t >= self.max_time:
                raise SchedulingError("max_time exceeded")

            running = {
                id(core.current_process)
                for core in self.cores
                if core.current_process is not None
            }

            ready = [
                p for p in self.processes
                if p.arrival_time <= t
                and not self.is_done(p)
                and id(p) not in running
            ]

            # ---------------- 1. Dispatch ----------------
            mapping = self.policy.schedule(t, ready, self.cores)
            self._validate(mapping, t)
            self._apply(mapping, t)

            # Waiting time = ticks spent arrived, unfinished and not running.
            for p in self.processes:
                if (
                    p.arrival_time <= t
                    and not self.is_done(p)
                    and not any(c.current_process is p for c in self.cores)
                ):
                    p.waiting_time += 1

            # ------ 2-4. Execute, thermal update, DVFS ------
            tick_rows = []

            for core in self.cores:
                task = core.current_process
                frequency_used = core.frequency

                if task is not None:
                    work = frequency_used / REFERENCE_FREQUENCY
                    task.remaining_time -= work
                    task.executed_work += work
                    task.busy_ticks += 1

                    if task.remaining_time < 1e-6:
                        task.remaining_time = 0

                    heat = core.thermal_model.calculate_heat(
                        task.workload_intensity, frequency_used
                    )
                else:
                    heat = 0.0

                core.update_temperature()
                self.governor.update(core)

                tick_rows.append({
                    "time": t + 1,
                    "core": core.core_id,
                    "core_type": core.core_type,
                    "pid": task.pid if task is not None else "",
                    "process": task.name if task is not None else "Idle",
                    "busy": int(task is not None),
                    "frequency_used": frequency_used,
                    "frequency_next": core.frequency,
                    "heat": heat,
                    "temperature": core.temperature,
                    "thermal_state": core.get_thermal_state(),
                })

            # ---------------- 5. Advance ----------------
            t += 1

            # ---------------- 6. Complete ----------------
            for core in self.cores:
                task = core.current_process

                if task is not None and task.remaining_time <= EPSILON:
                    task.completion_time = t
                    task.turnaround_time = t - task.arrival_time
                    task.deadline_missed = t > task.deadline
                    core.release_process()

            # ---------------- 7. Log ----------------
            self.trace.extend(tick_rows)

        return self.trace
