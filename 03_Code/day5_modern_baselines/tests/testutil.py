import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DAY5 = os.path.abspath(os.path.join(HERE, ".."))
CODE = os.path.abspath(os.path.join(DAY5, ".."))

for folder in (
    DAY5,
    os.path.join(CODE, "day1_basic_scheduler"),
    os.path.join(CODE, "day2_thermal_model"),
    os.path.join(CODE, "day3_thermos_scheduler"),
    os.path.join(CODE, "day4_experiments"),
):
    if folder not in sys.path:
        sys.path.append(folder)

from process import Process  # noqa: E402
from sim_engine import Simulator, create_cores, GOVERNORS  # noqa: E402


def task(pid, arrival, burst, deadline, priority=3, intensity=50, name=None):
    return Process(
        pid=pid,
        name=name or f"T{pid}",
        arrival_time=arrival,
        burst_time=burst,
        priority=priority,
        workload_intensity=intensity,
        task_type="Test",
        deadline=deadline,
    )


def run(policy, processes, num_cores=2, governor="off", thermal=None,
        initial_temperature=None):
    cores = create_cores(thermal)[:num_cores]

    if initial_temperature is not None:
        for core in cores:
            core.temperature = initial_temperature

    sim = Simulator(processes, cores, policy, GOVERNORS[governor]())
    trace = sim.run()
    return sim, trace


def by_pid(processes):
    return {p.pid: p for p in processes}


def executed_sequence(trace, core_id=1):
    """PID executed on `core_id` in each tick ('' = idle)."""
    return [row["pid"] for row in trace if row["core"] == core_id]
